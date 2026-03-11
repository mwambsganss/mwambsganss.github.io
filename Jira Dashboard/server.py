#!/usr/bin/env python3
"""Local dev server for Jira Executive Dashboard.

Serves static files and provides:
  GET    /api/auth-token        — returns current user's access token
  GET    /api/login             — starts Lilly SSO (Azure AD) OAuth2 flow
  GET    /api/callback          — handles OAuth2 redirect, stores session
  POST   /api/jira-proxy        — server-side proxy for Jira REST API (bypasses CORS)
  POST   /api/llm-proxy         — server-side proxy for LLM Gateway (bypasses CORS)
  GET    /api/llm-models        — lists available models from LLM gateway
  GET    /api/schedules         — list all saved schedules
  POST   /api/schedules         — create or update a schedule
  DELETE /api/schedules/<id>    — delete a schedule
  POST   /api/schedules/<id>/run — run a schedule immediately
  GET    /api/graph-auth-status  — whether Graph Mail.Send token is available
  POST   /api/email-test         — send a test email via Microsoft Graph
"""
import base64
import concurrent.futures
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load .env file if present (no third-party library needed)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())
import http.server
import json
import logging
import secrets
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid as uuid_mod
import ssl
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger("jira-dash")

PORT           = 8080
SERVE_DIR      = Path(__file__).parent
SCHEDULES_FILE   = SERVE_DIR / "schedules.json"
GRAPH_TOKEN_FILE = SERVE_DIR / "graph_token.json"

# Max issues fetched per project per scheduled run
MAX_ISSUES_PER_PROJECT = 2000
JIRA_PAGE_SIZE         = 100

# ── Lilly SSO / Azure AD config ───────────────────────────────────────────────
# Set these in a .env file or as environment variables (never hardcode secrets)
SSO_TENANT_ID     = os.getenv("SSO_TENANT_ID", "18a59a81-eea8-4c30-948a-d8824cdc2580")
SSO_CLIENT_ID     = os.getenv("SSO_CLIENT_ID", "82e22945-302c-4dc6-b961-54b937ff4c5f")
SSO_CLIENT_SECRET = os.getenv("SSO_CLIENT_SECRET", "FILL_IN_LILLY_CLIENT_SECRET")
SSO_REDIRECT_URI  = f"http://localhost:{PORT}/api/callback"
# Mail.Send lets the server call Graph /me/sendMail on behalf of the logged-in user.
# offline_access returns a refresh token so scheduled emails work after the 1-hour
# access token expires.
SSO_SCOPES       = "openid profile email offline_access https://graph.microsoft.com/Mail.Send"
SSO_CONFIGURED   = SSO_TENANT_ID != "FILL_IN_LILLY_TENANT_ID"

# ── Lilly internal SMTP relay config ──────────────────────────────────────────
# No auth required — works on Lilly network / VPN only.
# Zone options: smtp-z1-nomx.lilly.com, smtp-z2-nomx.lilly.com, smtp-z3-nomx.lilly.com
SMTP_RELAY_HOST = os.getenv("SMTP_RELAY_HOST", "smtp-z1-nomx.lilly.com")
SMTP_RELAY_PORT = int(os.getenv("SMTP_RELAY_PORT", "25"))

# In-memory session store (resets on server restart)
_sessions: dict = {}  # session_id  → {access_token, email, expires_at}
_pending:  dict = {}  # oauth_state → session_id  (CSRF guard)
_keychain: dict = {}  # cached keychain token so macOS only prompts once

# Lock protecting schedules.json reads/writes
_schedules_lock   = threading.Lock()
# Lock protecting graph_token.json reads/writes
_graph_token_lock = threading.Lock()

# Event used to wake the scheduler early (e.g. on shutdown)
_scheduler_wake = threading.Event()


# ── UTC helpers ───────────────────────────────────────────────────────────────

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC


# ── Schedule helpers ──────────────────────────────────────────────────────────

def _load_schedules() -> list:
    try:
        return json.loads(SCHEDULES_FILE.read_text()) if SCHEDULES_FILE.exists() else []
    except Exception:
        return []


def _save_schedules(schedules: list) -> None:
    SCHEDULES_FILE.write_text(json.dumps(schedules, indent=2))


def _compute_next_run(frequency: str, day_of_week: int) -> str:
    """Return ISO UTC datetime of the next scheduled run (8 AM UTC on target day).

    If today is the target day AND it is before 8 AM UTC, schedules for today.
    Otherwise schedules for the next occurrence of that weekday.
    """
    now = _utcnow()
    days_ahead = (day_of_week - now.weekday()) % 7
    if days_ahead == 0 and now.hour >= 8:
        days_ahead = 7   # today's window already passed; go to next week
    next_dt = (now + timedelta(days=days_ahead)).replace(
        hour=8, minute=0, second=0, microsecond=0
    )
    return next_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_range(frequency: str) -> tuple[str, str]:
    """Return (date_from, date_to) covering the reporting window."""
    now   = _utcnow()
    days  = {"weekly": 7, "biweekly": 14, "monthly": 30}.get(frequency, 7)
    start = now - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


# ── SSL contexts ──────────────────────────────────────────────────────────────

def _ssl_ctx_internal() -> ssl.SSLContext:
    """Relaxed SSL context for corporate internal hosts (Jira, LLM gateway).

    Lilly's internal services use a corporate CA not in Python's default bundle,
    so certificate verification is disabled for these proxy routes only.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
        ctx.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
    return ctx


def _ssl_ctx_external() -> ssl.SSLContext:
    """Verified SSL context for external endpoints (Microsoft Graph, Azure AD).

    Uses certifi's CA bundle if available — required on macOS python.org builds
    which ship without system root certificates baked in.
    """
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
        ctx.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
    return ctx


# ── Tenant ID helpers ─────────────────────────────────────────────────────────

def _decode_jwt_payload(token: str) -> dict:
    """Decode the payload of a JWT without verifying the signature.

    The signature is intentionally NOT verified here because this is used only
    to read non-sensitive metadata (tid, email) from tokens that were issued by
    Azure AD and stored locally.  Callers must not treat the result as
    authoritative for access-control decisions.
    """
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    try:
        return json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
    except Exception:
        return {}


def _get_effective_tenant_id() -> str:
    """Return SSO_TENANT_ID if configured, otherwise extract 'tid' from the keychain JWT."""
    if SSO_TENANT_ID != "FILL_IN_LILLY_TENANT_ID":
        return SSO_TENANT_ID
    token = _keychain.get("token", "")
    if not token:
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "lilly-code", "-w"],
                capture_output=True, text=True, check=True,
            )
            raw = result.stdout.strip()
            try:
                token = json.loads(raw).get("access_token", "")
            except Exception:
                token = raw
        except Exception:
            pass
    if token:
        payload = _decode_jwt_payload(token)
        tid = payload.get("tid", "")
        if tid:
            return tid
    return ""


def _email_from_jwt(token: str) -> str:
    payload = _decode_jwt_payload(token)
    return (
        payload.get("preferred_username")
        or payload.get("upn")
        or payload.get("email")
        or ""
    )


# ── Email delivery via Lilly internal SMTP relay ─────────────────────────────

def _send_via_smtp_relay(subject: str, html_body: str, recipients: list,
                         from_email: str) -> str:
    """Send email via Lilly internal SMTP relay (no auth, no TLS).

    Requires Lilly network or VPN.  Uses smtp-z1-nomx.lilly.com:25 by default;
    override with SMTP_RELAY_HOST / SMTP_RELAY_PORT env vars.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_email
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))
    try:
        with smtplib.SMTP(SMTP_RELAY_HOST, SMTP_RELAY_PORT, timeout=10) as smtp:
            smtp.sendmail(from_email, recipients, msg.as_string())
        log.info("SMTP relay email sent to %d recipients via %s",
                 len(recipients), SMTP_RELAY_HOST)
        return f"Sent to {len(recipients)} recipient(s) via SMTP relay ({SMTP_RELAY_HOST})"
    except Exception as e:
        log.error("SMTP relay send failed: %s", e)
        return f"SMTP relay failed: {repr(e)}"


# ── Email delivery via Microsoft Graph ───────────────────────────────────────

def _load_graph_token() -> dict:
    try:
        return json.loads(GRAPH_TOKEN_FILE.read_text()) if GRAPH_TOKEN_FILE.exists() else {}
    except Exception:
        return {}


def _save_graph_token(data: dict) -> None:
    GRAPH_TOKEN_FILE.write_text(json.dumps(data, indent=2))


def _get_valid_graph_token() -> str:
    """Return a valid Graph access token, refreshing via stored refresh token if needed."""
    with _graph_token_lock:
        tok = _load_graph_token()
    if not tok:
        return ""
    # Return existing token if not yet expired (with 60 s buffer)
    expires_at = tok.get("expires_at", "")
    if expires_at:
        try:
            exp = datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ")
            if _utcnow() < exp - timedelta(seconds=60):
                return tok.get("access_token", "")
        except ValueError:
            pass
    # Refresh
    refresh_token = tok.get("refresh_token", "")
    if not refresh_token:
        return ""
    try:
        token_url  = f"https://login.microsoftonline.com/{SSO_TENANT_ID}/oauth2/v2.0/token"
        token_body = urllib.parse.urlencode({
            "client_id":     SSO_CLIENT_ID,
            "client_secret": SSO_CLIENT_SECRET,
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "scope":         "https://graph.microsoft.com/Mail.Send offline_access",
        }).encode()
        req = urllib.request.Request(
            token_url, data=token_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, context=_ssl_ctx_external()) as resp:
            new_tok = json.loads(resp.read())
        expires_in = new_tok.get("expires_in", 3600)
        new_tok["expires_at"] = (
            _utcnow() + timedelta(seconds=expires_in)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        with _graph_token_lock:
            _save_graph_token(new_tok)
        log.info("Graph token refreshed successfully")
        return new_tok.get("access_token", "")
    except Exception as e:
        log.error("Graph token refresh failed: %s", e)
        return ""


def _send_via_graph(subject: str, html_body: str, recipients: list) -> str:
    """Send email via Microsoft Graph /me/sendMail using the stored delegated token."""
    access_token = _get_valid_graph_token()
    if not access_token:
        return "Email not sent — sign in at /api/login to authorize email sending (needed once)"

    payload = json.dumps({
        "message": {
            "subject": subject,
            "body":    {"contentType": "HTML", "content": html_body},
            "toRecipients": [
                {"emailAddress": {"address": r}} for r in recipients
            ],
        },
        "saveToSentItems": True,
    }).encode()
    req = urllib.request.Request(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        data=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx_external()) as resp:
            resp.read()
        log.info("Graph email sent to %d recipients", len(recipients))
        return f"Sent to {len(recipients)} recipient(s) via Microsoft Graph"
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        log.error("Graph send HTTP error %s: %s", e.code, msg)
        return f"Graph send failed: HTTP {e.code} — {msg}"
    except Exception as e:
        log.error("Graph send failed: %s", e)
        return f"Graph send failed: {repr(e)}"


# ── Jira fetch helpers ────────────────────────────────────────────────────────

def _fetch_project_issues(jira_base: str, auth: str, proj_key: str,
                          date_from: str, date_to: str,
                          ctx: ssl.SSLContext) -> list:
    """Fetch up to MAX_ISSUES_PER_PROJECT issues for one project. Returns list of dicts."""
    issues     = []
    next_token = None
    fetched    = 0
    while fetched < MAX_ISSUES_PER_PROJECT:
        jql    = f'project = {proj_key} AND updated >= "{date_from}" AND updated <= "{date_to}" ORDER BY updated DESC'
        params = urllib.parse.urlencode({
            "jql": jql, "maxResults": JIRA_PAGE_SIZE,
            "fields": "summary,status,issuetype,priority,assignee,updated",
        })
        if next_token:
            params += "&nextPageToken=" + urllib.parse.quote(next_token)
        try:
            req = urllib.request.Request(
                f"{jira_base}/rest/api/3/search/jql?{params}",
                headers={"Authorization": auth, "Accept": "application/json"},
            )
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = json.loads(resp.read())
            page = data.get("issues") or data.get("values") or []
            for issue in page:
                f = issue.get("fields", {})
                issues.append({
                    "key":       issue.get("key", ""),
                    "project":   proj_key,
                    "summary":   f.get("summary", ""),
                    "status":    (f.get("status") or {}).get("name", ""),
                    "issueType": (f.get("issuetype") or {}).get("name", ""),
                    "priority":  (f.get("priority") or {}).get("name", ""),
                    "assignee":  (f.get("assignee") or {}).get("displayName", "Unassigned"),
                    "updated":   (f.get("updated") or "")[:10],
                })
            fetched   += len(page)
            next_token = data.get("nextPageToken")
            if not next_token or not page:
                break
        except Exception as e:
            log.warning("Jira fetch error for %s: %s", proj_key, e)
            break
    return issues


# ── Schedule runner ───────────────────────────────────────────────────────────

def run_schedule(schedule: dict) -> str:
    """Fetch Jira issues, generate LLM summary, send email. Returns status string."""
    jira_base    = schedule.get("jiraBaseUrl", "").rstrip("/")
    jira_email   = schedule.get("jiraEmail", "")
    jira_token   = schedule.get("jiraToken", "")
    projects     = [p for p in schedule.get("projects", []) if p.get("selected", True)]
    llm_url      = schedule.get("llmUrl", "").rstrip("/")
    llm_key      = schedule.get("llmKey", "")
    llm_model    = schedule.get("llmModel", "")
    recipients   = schedule.get("recipients", [])
    frequency    = schedule.get("frequency", "weekly")

    if not all([jira_base, jira_email, jira_token, projects, llm_url, llm_key, recipients]):
        return "Missing required configuration"

    date_from, date_to = _date_range(frequency)
    auth = "Basic " + base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
    ctx  = _ssl_ctx_internal()

    # ── Fetch Jira issues in parallel ────────────────────────────────
    all_issues: list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(projects), 8)) as pool:
        futures = {
            pool.submit(_fetch_project_issues, jira_base, auth, p["key"], date_from, date_to, ctx): p["key"]
            for p in projects
        }
        for future in concurrent.futures.as_completed(futures):
            proj_key = futures[future]
            try:
                all_issues.extend(future.result())
            except Exception as e:
                log.warning("Project %s fetch failed: %s", proj_key, e)

    if not all_issues:
        return f"No issues found for {date_from} → {date_to}"

    # ── Build LLM prompt ─────────────────────────────────────────────
    freq_label    = {"weekly": "weekly", "biweekly": "bi-weekly", "monthly": "monthly"}.get(frequency, "")
    project_names = ", ".join(p["key"] for p in projects)
    status_counts: dict = {}
    for i in all_issues:
        status_counts[i["status"]] = status_counts.get(i["status"], 0) + 1
    status_str  = ", ".join(f"{v} {k}" for k, v in sorted(status_counts.items(), key=lambda x: -x[1]))
    issue_lines = "\n".join(
        f"- [{i['key']}] {i['summary']} | {i['status']} | {i['assignee']} | {i['updated']}"
        for i in all_issues[:200]
    )
    prompt = (
        f"You are an executive assistant generating a {freq_label} Jira portfolio summary for Lilly.\n\n"
        f"Date range: {date_from} to {date_to}\nProjects: {project_names}\n"
        f"Total issues: {len(all_issues)}\nStatus breakdown: {status_str}\n\n"
        f"Issues:\n{issue_lines}\n\n"
        "Write a concise executive summary for senior leadership using this exact structure:\n\n"
        "## Overall Health\n"
        "- bullet points about portfolio health and key metrics\n\n"
        "## Progress This Period\n"
        "- bullet points about completed work and momentum\n\n"
        "## Risks & Blockers\n"
        "- bullet points about overdue items, blockers, and capacity concerns\n\n"
        "## Recommended Actions\n"
        "- 2-3 specific, actionable recommendations for leadership\n\n"
        "Use markdown: ## for section headings, - for bullet points, **bold** for emphasis. "
        "Keep bullets concise (one line each). No prose paragraphs."
    )

    # ── Call LLM ─────────────────────────────────────────────────────
    try:
        req = urllib.request.Request(
            llm_url + "/v1/messages",
            data=json.dumps({
                "model": llm_model, "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }).encode(),
            headers={
                "Authorization": f"Bearer {llm_key}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, context=ctx) as resp:
            llm_data     = json.loads(resp.read())
        summary_text = llm_data.get("content", [{}])[0].get("text", "")
    except Exception as e:
        summary_text = f"[LLM summary unavailable: {e}]"
        log.warning("LLM call failed for schedule '%s': %s", schedule.get("name"), e)

    # ── Build and send email ──────────────────────────────────────────
    result = _build_and_send_email(
        schedule_name=schedule.get("name", "Jira Executive Summary"),
        freq_label=freq_label, date_from=date_from, date_to=date_to,
        project_names=project_names, total_issues=len(all_issues),
        summary_text=summary_text, recipients=recipients,
        from_email=jira_email,
    )
    log.info("Schedule '%s' completed: %s", schedule.get("name"), result)
    return result


def _build_and_send_email(*, schedule_name: str, freq_label: str,
                           date_from: str, date_to: str, project_names: str,
                           total_issues: int, summary_text: str,
                           recipients: list, from_email: str = "") -> str:
    """Construct the HTML email and deliver.

    Tries the Lilly internal SMTP relay first (no auth, requires network/VPN).
    Falls back to Microsoft Graph if a stored delegated token is available.
    """
    subject = f"{schedule_name} — {date_from} to {date_to}"

    # Convert markdown from LLM output into styled HTML sections for the email.
    # Only allow a safe subset of tags; strip everything else.
    import re as _re

    def _md_to_email_html(md: str) -> str:
        # Strip any raw HTML tags the LLM may have injected
        md = _re.sub(r"<[^>]+>", "", md)
        lines = md.split("\n")
        out   = []
        in_ul = False
        for line in lines:
            # Bold headings: **Heading** or ## Heading
            h2 = _re.match(r"^#{1,3}\s+(.+)", line)
            bold_heading = _re.match(r"^\*\*(.+?)\*\*\s*[:\-—]?\s*$", line)
            bullet = _re.match(r"^[\-\*]\s+(.+)", line)
            bold_inline = lambda s: _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

            if h2 or bold_heading:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                text = (h2.group(1) if h2 else bold_heading.group(1)).strip(" *:")
                out.append(
                    f'<div style="margin:20px 0 6px;padding:8px 12px;'
                    f'background:#f0f4f8;border-left:4px solid #C8102E;'
                    f'font-size:13px;font-weight:700;color:#1A1A1A;'
                    f'letter-spacing:.3px;text-transform:uppercase">{text}</div>'
                )
            elif bullet:
                if not in_ul:
                    out.append('<ul style="margin:4px 0 8px 0;padding-left:20px">')
                    in_ul = True
                out.append(
                    f'<li style="margin:4px 0;font-size:14px;line-height:1.6;color:#2D2D2D">'
                    f'{bold_inline(bullet.group(1))}</li>'
                )
            elif line.strip():
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                out.append(
                    f'<p style="margin:6px 0;font-size:14px;line-height:1.7;color:#2D2D2D">'
                    f'{bold_inline(line.strip())}</p>'
                )
            else:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
        if in_ul:
            out.append("</ul>")
        return "\n".join(out)

    summary_html = _md_to_email_html(summary_text)

    html_body = f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;color:#1A1A1A;background:#F4F4F4">
  <!-- Header -->
  <div style="background:#C8102E;padding:24px 28px;color:#fff">
    <div style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;opacity:.75;margin-bottom:4px">Lilly Enterprise Automation</div>
    <div style="font-size:20px;font-weight:700;margin:0">{freq_label.title()} Portfolio Briefing</div>
    <div style="font-size:13px;opacity:.85;margin-top:6px">{date_from} &ndash; {date_to}</div>
  </div>
  <!-- Meta bar -->
  <div style="background:#1A1A1A;padding:10px 28px;display:flex;gap:24px">
    <span style="font-size:12px;color:#aaa">Projects: <strong style="color:#fff">{project_names}</strong></span>
    <span style="font-size:12px;color:#aaa">Issues: <strong style="color:#fff">{total_issues}</strong></span>
  </div>
  <!-- Body -->
  <div style="background:#fff;padding:24px 28px;border:1px solid #E0E0E0;border-top:none">
    {summary_html}
  </div>
  <!-- Footer -->
  <div style="padding:14px 28px;background:#F4F4F4;border-top:1px solid #E0E0E0;font-size:11px;color:#999">
    Generated by Jira Executive Dashboard &middot; Lilly LLM Gateway
  </div>
</body></html>"""

    if from_email:
        return _send_via_smtp_relay(subject, html_body, recipients, from_email)
    return _send_via_graph(subject, html_body, recipients)


# ── Background scheduler ──────────────────────────────────────────────────────

def _scheduler_loop() -> None:
    """Background daemon: check every 60 s for overdue schedules and run them."""
    while True:
        # Use Event.wait so the loop can be woken early on shutdown
        _scheduler_wake.wait(timeout=60)
        _scheduler_wake.clear()
        try:
            with _schedules_lock:
                schedules = _load_schedules()
            now     = _utcnow()
            changed = False
            for sched in schedules:
                if not sched.get("enabled", True):
                    continue
                next_run_str = sched.get("nextRun", "")
                if not next_run_str:
                    continue
                try:
                    next_run = datetime.strptime(next_run_str, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    continue
                if now >= next_run:
                    log.info("Running schedule '%s'", sched.get("name"))
                    status = run_schedule(sched)
                    freq   = sched.get("frequency", "weekly")
                    days   = {"weekly": 7, "biweekly": 14, "monthly": 30}.get(freq, 7)
                    sched["lastRun"]    = now.strftime("%Y-%m-%dT%H:%M:%SZ")
                    sched["lastStatus"] = status
                    sched["nextRun"]    = (next_run + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    changed = True
            if changed:
                with _schedules_lock:
                    _save_schedules(schedules)
        except Exception as e:
            log.error("Scheduler loop error: %s", e)


# ── HTTP Handler ──────────────────────────────────────────────────────────────

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    # ── Routing ───────────────────────────────────────────────────────────────

    def do_POST(self):
        if self.path == "/api/jira-proxy":
            self._proxy_jira()
        elif self.path == "/api/llm-proxy":
            self._proxy_llm()
        elif self.path == "/api/schedules":
            self._upsert_schedule()
        elif self.path.startswith("/api/schedules/") and self.path.endswith("/run"):
            self._run_schedule_now()
        elif self.path == "/api/email-test":
            self._test_email()
        else:
            self._error(404, "Not found")

    def do_GET(self):
        if self.path == "/api/auth-token":
            self._serve_auth_token()
        elif self.path == "/api/login":
            self._start_sso_login()
        elif self.path.startswith("/api/callback"):
            self._handle_sso_callback()
        elif self.path.startswith("/api/llm-models"):
            self._serve_llm_models()
        elif self.path == "/api/schedules":
            self._list_schedules()
        elif self.path == "/api/graph-auth-status":
            self._serve_graph_auth_status()
        else:
            super().do_GET()

    def do_DELETE(self):
        if self.path.startswith("/api/schedules/"):
            self._delete_schedule()
        else:
            self._error(404, "Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ── SSO / Auth ────────────────────────────────────────────────────────────

    def _start_sso_login(self):
        if not SSO_CONFIGURED:
            self._error(501, "SSO not configured — fill in SSO_TENANT_ID and SSO_CLIENT_ID in server.py")
            return
        state      = secrets.token_urlsafe(16)
        session_id = secrets.token_urlsafe(32)
        _pending[state] = session_id
        params = urllib.parse.urlencode({
            "client_id":     SSO_CLIENT_ID,
            "response_type": "code",
            "redirect_uri":  SSO_REDIRECT_URI,
            "response_mode": "query",
            "scope":         SSO_SCOPES,
            "state":         state,
        })
        auth_url = (
            f"https://login.microsoftonline.com/{SSO_TENANT_ID}"
            f"/oauth2/v2.0/authorize?{params}"
        )
        self.send_response(302)
        self.send_header("Location", auth_url)
        self.send_header("Set-Cookie", f"session={session_id}; HttpOnly; SameSite=Lax; Path=/")
        self._cors_headers()
        self.end_headers()

    def _handle_sso_callback(self):
        qs    = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code  = qs.get("code",  [None])[0]
        state = qs.get("state", [None])[0]
        error = qs.get("error", [None])[0]

        if error:
            self._error(401, f"SSO error: {qs.get('error_description', [error])[0]}")
            return
        session_id = _pending.pop(state, None)
        if not session_id or not code:
            self._error(400, "Invalid OAuth callback — state mismatch or missing code")
            return

        token_url  = f"https://login.microsoftonline.com/{SSO_TENANT_ID}/oauth2/v2.0/token"
        token_body = urllib.parse.urlencode({
            "client_id":     SSO_CLIENT_ID,
            "client_secret": SSO_CLIENT_SECRET,
            "code":          code,
            "redirect_uri":  SSO_REDIRECT_URI,
            "grant_type":    "authorization_code",
            "scope":         SSO_SCOPES,
        }).encode()
        try:
            req = urllib.request.Request(
                token_url, data=token_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            with urllib.request.urlopen(req, context=_ssl_ctx_external()) as resp:
                token_json = json.loads(resp.read())
        except Exception as e:
            self._error(500, f"Token exchange failed: {e}")
            return

        access_token  = token_json.get("access_token", "")
        refresh_token = token_json.get("refresh_token", "")
        expires_in    = token_json.get("expires_in", 3600)
        expires_at    = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + expires_in))
        email_addr    = _email_from_jwt(access_token)

        _sessions[session_id] = {
            "access_token": access_token,
            "email":        email_addr,
            "expires_at":   expires_at,
        }

        # Persist Graph token so scheduled email runs can use it after the session expires
        if refresh_token:
            with _graph_token_lock:
                _save_graph_token({
                    "access_token":  access_token,
                    "refresh_token": refresh_token,
                    "expires_at":    expires_at,
                    "email":         email_addr,
                })
            log.info("Graph Mail.Send token saved for %s", email_addr)

        self.send_response(302)
        self.send_header("Location", "/dashboard.html")
        self.send_header("Set-Cookie", f"session={session_id}; HttpOnly; SameSite=Lax; Path=/")
        self._cors_headers()
        self.end_headers()

    def _serve_auth_token(self):
        cookies = {}
        for part in self.headers.get("Cookie", "").split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookies[k.strip()] = v.strip()
        session = _sessions.get(cookies.get("session", ""))
        if session and session.get("access_token"):
            self._json(200, {
                "token":      session["access_token"],
                "expires_at": session["expires_at"],
                "email":      session["email"],
            })
            return

        if _keychain:
            self._json(200, _keychain)
            return
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "lilly-code", "-w"],
                capture_output=True, text=True, check=True,
            )
            data       = json.loads(result.stdout.strip())
            token      = data.get("access_token", "")
            expires_at = data.get("expires_at", "")
            email_addr = _email_from_jwt(token)
            _keychain.update({"token": token, "expires_at": expires_at, "email": email_addr})
            self._json(200, _keychain)
        except subprocess.CalledProcessError:
            if SSO_CONFIGURED:
                self._json(401, {"error": "Not authenticated", "login_url": "/api/login"})
            else:
                self._error(401, "Not authenticated — run: lilly-code login")
        except Exception as e:
            self._error(500, str(e))

    # ── Schedule CRUD ─────────────────────────────────────────────────────────

    def _list_schedules(self):
        with _schedules_lock:
            self._json(200, {"schedules": _load_schedules()})

    def _upsert_schedule(self):
        length    = int(self.headers.get("Content-Length", 0))
        body      = json.loads(self.rfile.read(length))
        with _schedules_lock:
            schedules = _load_schedules()
            sched_id  = body.get("id")
            if sched_id:
                for i, s in enumerate(schedules):
                    if s["id"] == sched_id:
                        schedules[i] = body
                        break
                else:
                    schedules.append(body)
            else:
                body["id"]        = str(uuid_mod.uuid4())
                body["createdAt"] = _utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                body["nextRun"]   = _compute_next_run(body.get("frequency", "weekly"), body.get("dayOfWeek", 4))
                body.setdefault("enabled", True)
                schedules.append(body)
            _save_schedules(schedules)
        self._json(200, body)

    def _delete_schedule(self):
        sched_id = self.path.split("/")[-1]
        with _schedules_lock:
            schedules = [s for s in _load_schedules() if s.get("id") != sched_id]
            _save_schedules(schedules)
        self._json(200, {"ok": True})

    def _serve_graph_auth_status(self):
        tok = _load_graph_token()
        if tok.get("refresh_token"):
            self._json(200, {
                "authorized": True,
                "email": tok.get("email", ""),
                "expires_at": tok.get("expires_at", ""),
            })
        else:
            self._json(200, {"authorized": False})

    def _test_email(self):
        length  = int(self.headers.get("Content-Length", 0))
        body    = json.loads(self.rfile.read(length))
        recipients = body.get("recipients", [])
        if not recipients:
            self._json(200, {"ok": False, "msg": "No recipients provided"})
            return
        sample_md = (
            "## Overall Health\n"
            "- Portfolio is **on track** — this is a test email from the Jira Dashboard\n"
            "- Email formatting and delivery confirmed working\n\n"
            "## Recommended Actions\n"
            "- No action needed — this is a test\n"
        )
        from_email = (
            body.get("fromEmail", "")
            or _load_graph_token().get("email", "")
            or _keychain.get("email", "")
            or next((s.get("jiraEmail", "") for s in _load_schedules() if s.get("jiraEmail")), "")
        )
        if not from_email:
            self._json(200, {"ok": False, "msg": "No sender address available — add jiraEmail to a schedule or pass fromEmail in the request"})
            return
        result = _build_and_send_email(
            schedule_name="Email Test",
            freq_label="test",
            date_from="—",
            date_to="—",
            project_names="Test",
            total_issues=0,
            summary_text=sample_md,
            recipients=recipients,
            from_email=from_email,
        )
        ok = result.startswith("Sent")
        self._json(200, {"ok": ok, "msg": result})

    def _run_schedule_now(self):
        sched_id = self.path.split("/")[-2]
        with _schedules_lock:
            schedules = _load_schedules()
        for sched in schedules:
            if sched.get("id") == sched_id:
                status = run_schedule(sched)
                sched["lastRun"]    = _utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                sched["lastStatus"] = status
                with _schedules_lock:
                    _save_schedules(schedules)
                self._json(200, {"status": status})
                return
        self._error(404, "Schedule not found")

    # ── Proxies ───────────────────────────────────────────────────────────────

    def _serve_llm_models(self):
        qs     = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token  = qs.get("token", [None])[0] or ""
        url    = qs.get("url", ["https://lilly-code-server.api.gateway.llm.lilly.com"])[0]
        target = url.rstrip("/") + "/v1/models"
        req    = urllib.request.Request(
            target,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        ctx = self._ssl_ctx()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = json.loads(resp.read())
            models = [m["id"] for m in data.get("data", []) if "id" in m]
            if not models:
                models = [m.get("id") or m for m in data.get("models", data if isinstance(data, list) else [])]
            self._json(200, {"models": sorted(models)})
        except urllib.error.HTTPError as e:
            self._error(e.code, e.read().decode()[:300])
        except Exception as e:
            self._error(500, str(e))

    def _proxy_jira(self):
        length     = int(self.headers.get("Content-Length", 0))
        body       = json.loads(self.rfile.read(length))
        target_url = body.get("url", "")
        headers    = body.get("headers", {})
        req        = urllib.request.Request(target_url, headers=headers)
        ctx        = self._ssl_ctx()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            self._raw(200, data)
        except urllib.error.HTTPError as e:
            self._error(e.code, e.read().decode()[:300])
        except Exception as e:
            self._error(500, str(e))

    def _proxy_llm(self):
        length      = int(self.headers.get("Content-Length", 0))
        body        = json.loads(self.rfile.read(length))
        target_url  = body.get("url", "")
        req_headers = body.get("headers", {})
        req_body    = json.dumps(body.get("body", {})).encode()
        req         = urllib.request.Request(
            target_url, data=req_body, headers=req_headers, method="POST"
        )
        ctx = self._ssl_ctx()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            self._raw(200, data)
        except urllib.error.HTTPError as e:
            self._error(e.code, e.read().decode()[:500])
        except Exception as e:
            self._error(500, str(e))

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _ssl_ctx() -> ssl.SSLContext:
        return _ssl_ctx_internal()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _raw(self, code: int, data: bytes):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _error(self, code: int, message: str):
        self._json(code, {"error": message})

    def log_message(self, fmt, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    threading.Thread(target=_scheduler_loop, daemon=True).start()

    print(f"Dashboard → http://localhost:{PORT}/dashboard.html")
    if SSO_CONFIGURED:
        print(f"  SSO enabled  — sign in at http://localhost:{PORT}/api/login")
    else:
        print("  SSO not configured — using lilly-code keychain fallback")
        print("  To enable SSO: fill in SSO_TENANT_ID and SSO_CLIENT_ID in server.py")
    print(f"  Scheduler running — checks every 60 s for due email schedules")
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
