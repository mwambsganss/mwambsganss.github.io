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
"""
import base64
import concurrent.futures
import email.mime.multipart
import email.mime.text
import http.server
import json
import logging
import secrets
import smtplib
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
SCHEDULES_FILE = SERVE_DIR / "schedules.json"

# Max issues fetched per project per scheduled run
MAX_ISSUES_PER_PROJECT = 2000
JIRA_PAGE_SIZE         = 100

# ── Lilly SSO / Azure AD config ───────────────────────────────────────────────
SSO_TENANT_ID    = "18a59a81-eea8-4c30-948a-d8824cdc2580"
SSO_CLIENT_ID    = "82e22945-302c-4dc6-b961-54b937ff4c5f"
SSO_REDIRECT_URI = f"http://localhost:{PORT}/api/callback"
SSO_SCOPES       = "openid profile email offline_access"
SSO_CONFIGURED   = SSO_TENANT_ID != "FILL_IN_LILLY_TENANT_ID"

# In-memory session store (resets on server restart)
_sessions: dict = {}  # session_id  → {access_token, email, expires_at}
_pending:  dict = {}  # oauth_state → session_id  (CSRF guard)
_keychain: dict = {}  # cached keychain token so macOS only prompts once
_graph_token:   dict = {}   # {access_token, refresh_token, email, expires_at}
_graph_pending: dict = {}   # oauth_state → True  (CSRF guard)
GRAPH_SCOPES       = "Mail.Send offline_access openid profile email"
GRAPH_REDIRECT_URI = f"http://localhost:{PORT}/api/graph-callback"

# Lock protecting schedules.json reads/writes and _graph_token mutation
_schedules_lock = threading.Lock()
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
    """Verified SSL context for external endpoints (Microsoft Graph, Azure AD)."""
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


# ── Graph API helpers ─────────────────────────────────────────────────────────

def _graph_configured() -> bool:
    return bool(_get_effective_tenant_id()) and SSO_CLIENT_ID != "FILL_IN_CLIENT_ID"


def _graph_token_valid() -> bool:
    with _graph_token_lock:
        if not _graph_token.get("access_token"):
            return False
        exp = _graph_token.get("expires_at", "")
    try:
        return datetime.strptime(exp, "%Y-%m-%dT%H:%M:%SZ") > _utcnow()
    except Exception:
        return True   # assume valid if we can't parse expiry


def _refresh_graph_if_needed() -> bool:
    """Refresh the Graph access token using the stored refresh token. Returns True if now valid."""
    if _graph_token_valid():
        return True
    with _graph_token_lock:
        refresh = _graph_token.get("refresh_token", "")
    if not refresh:
        log.warning("Graph refresh failed: no refresh token stored")
        return False
    tenant_id = _get_effective_tenant_id()
    if not tenant_id:
        log.warning("Graph refresh failed: cannot determine tenant ID")
        return False
    try:
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        body = urllib.parse.urlencode({
            "client_id":     SSO_CLIENT_ID,
            "refresh_token": refresh,
            "grant_type":    "refresh_token",
            "scope":         GRAPH_SCOPES,
        }).encode()
        req = urllib.request.Request(
            token_url, data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        with _graph_token_lock:
            _graph_token["access_token"]  = data.get("access_token", "")
            _graph_token["refresh_token"] = data.get("refresh_token", refresh)
            _graph_token["expires_at"]    = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + data.get("expires_in", 3600))
            )
        ok = bool(_graph_token.get("access_token"))
        if not ok:
            log.warning("Graph refresh returned no access_token")
        return ok
    except urllib.error.HTTPError as e:
        log.error("Graph refresh HTTP error %s: %s", e.code, e.read().decode()[:200])
        return False
    except Exception as e:
        log.error("Graph refresh failed: %s", e)
        return False


def _send_via_graph(subject: str, html_body: str, recipients: list) -> str:
    """Send email via Microsoft Graph API /me/sendMail."""
    if not _refresh_graph_if_needed():
        return "Email failed: Microsoft account not connected — open Settings > Schedules and click Connect Microsoft Account"
    with _graph_token_lock:
        access_token = _graph_token.get("access_token", "")
    payload = {
        "message": {
            "subject": subject,
            "body":    {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"address": r}} for r in recipients],
        },
        "saveToSentItems": False,
    }
    req = urllib.request.Request(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {access_token}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()   # 202 Accepted = success
        log.info("Graph email sent to %d recipients", len(recipients))
        return f"Sent to {len(recipients)} recipient(s) via Microsoft Graph"
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:300]
        log.error("Graph send HTTP error %s: %s", e.code, msg)
        return f"Graph send failed: {e.code} {msg}"
    except Exception as e:
        log.error("Graph send failed: %s", e)
        return f"Graph send failed: {e}"


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
    jira_base  = schedule.get("jiraBaseUrl", "").rstrip("/")
    jira_email = schedule.get("jiraEmail", "")
    jira_token = schedule.get("jiraToken", "")
    projects   = [p for p in schedule.get("projects", []) if p.get("selected", True)]
    llm_url    = schedule.get("llmUrl", "").rstrip("/")
    llm_key    = schedule.get("llmKey", "")
    llm_model  = schedule.get("llmModel", "")
    recipients = schedule.get("recipients", [])
    frequency  = schedule.get("frequency", "weekly")
    smtp_host  = schedule.get("smtpHost", "smtp.office365.com")
    smtp_port  = int(schedule.get("smtpPort", 587))
    smtp_user  = schedule.get("smtpUser", "")
    smtp_pass  = schedule.get("smtpPassword", "")
    from_email = schedule.get("fromEmail", "")

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
        "Write a concise executive summary (3-5 paragraphs) covering: overall portfolio health, "
        "key accomplishments, in-progress items and blockers, items at risk, and recommended next steps. "
        "Keep it professional and suitable for senior leadership."
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
        smtp_host=smtp_host, smtp_port=smtp_port,
        smtp_user=smtp_user, smtp_pass=smtp_pass, from_email=from_email,
    )
    log.info("Schedule '%s' completed: %s", schedule.get("name"), result)
    return result


def _build_and_send_email(*, schedule_name: str, freq_label: str,
                           date_from: str, date_to: str, project_names: str,
                           total_issues: int, summary_text: str,
                           recipients: list, smtp_host: str, smtp_port: int,
                           smtp_user: str, smtp_pass: str, from_email: str) -> str:
    """Construct the HTML email and send it via Graph API or SMTP fallback."""
    subject = f"{schedule_name} — {date_from} to {date_to}"

    # Sanitize LLM output: strip HTML tags before embedding in email body
    import re as _re
    safe_summary = _re.sub(r"<[^>]+>", "", summary_text)

    html_body = f"""<html><body style="font-family:Arial,sans-serif;max-width:800px;margin:0 auto;color:#1A1A1A">
  <div style="background:#C8102E;padding:20px;color:#fff">
    <h1 style="margin:0;font-size:20px">Lilly Enterprise Automation</h1>
    <p style="margin:4px 0 0;font-size:14px;opacity:.85">{freq_label.title()} Portfolio Briefing &middot; {date_from} to {date_to}</p>
  </div>
  <div style="padding:24px;background:#fff;border:1px solid #E8E8E8">
    <p style="margin:0 0 16px;font-size:13px;color:#6B6B6B">Projects: <strong>{project_names}</strong> &middot; {total_issues} issues</p>
    <div style="white-space:pre-wrap;line-height:1.7;font-size:14px">{safe_summary}</div>
  </div>
  <div style="padding:16px;background:#F5F5F5;border-top:1px solid #E8E8E8;font-size:11px;color:#6B6B6B">
    Generated by Jira Executive Dashboard &middot; Lilly LLM Gateway
  </div>
</body></html>"""

    # Prefer Microsoft Graph API (no SMTP auth required); fall back to SMTP
    if _graph_token.get("access_token") or _graph_token.get("refresh_token"):
        return _send_via_graph(subject, html_body, recipients)

    # SMTP fallback
    msg = email.mime.multipart.MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_email
    msg["To"]      = ", ".join(recipients)
    msg.attach(email.mime.text.MIMEText(
        f"Lilly Enterprise Automation — {freq_label.title()} Portfolio Briefing\n"
        f"{date_from} to {date_to}\nProjects: {project_names}\n\n{safe_summary}", "plain"
    ))
    msg.attach(email.mime.text.MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            if smtp_user and smtp_pass:
                smtp.login(smtp_user, smtp_pass)
            smtp.sendmail(from_email, recipients, msg.as_string())
        return f"Sent to {len(recipients)} recipient(s)"
    except Exception as e:
        return f"Email failed: {e}"


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
        elif self.path == "/api/smtp-test":
            self._test_smtp()
        else:
            self._error(404, "Not found")

    def do_GET(self):
        if self.path == "/api/auth-token":
            self._serve_auth_token()
        elif self.path == "/api/login":
            self._start_sso_login()
        elif self.path.startswith("/api/callback"):
            self._handle_sso_callback()
        elif self.path == "/api/graph-login":
            self._start_graph_login()
        elif self.path.startswith("/api/graph-callback"):
            self._handle_graph_callback()
        elif self.path == "/api/graph-status":
            self._serve_graph_status()
        elif self.path.startswith("/api/llm-models"):
            self._serve_llm_models()
        elif self.path == "/api/schedules":
            self._list_schedules()
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
            "client_id":    SSO_CLIENT_ID,
            "code":         code,
            "redirect_uri": SSO_REDIRECT_URI,
            "grant_type":   "authorization_code",
            "scope":        SSO_SCOPES,
        }).encode()
        try:
            req = urllib.request.Request(
                token_url, data=token_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            with urllib.request.urlopen(req) as resp:
                token_json = json.loads(resp.read())
        except Exception as e:
            self._error(500, f"Token exchange failed: {e}")
            return

        access_token = token_json.get("access_token", "")
        expires_in   = token_json.get("expires_in", 3600)
        email_addr   = _email_from_jwt(access_token)

        _sessions[session_id] = {
            "access_token": access_token,
            "email":        email_addr,
            "expires_at":   time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + expires_in)
            ),
        }

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

    # ── Graph API auth ────────────────────────────────────────────────────────

    def _start_graph_login(self):
        if not _graph_configured():
            tenant_id = _get_effective_tenant_id()
            if not tenant_id:
                self._error(501, "Cannot detect tenant ID — run: lilly-code login, then retry")
            else:
                self._error(501, f"SSO_CLIENT_ID not configured — set it in server.py (tenant auto-detected: {tenant_id})")
            return
        state = secrets.token_urlsafe(16)
        _graph_pending[state] = True
        tenant_id = _get_effective_tenant_id()
        params = urllib.parse.urlencode({
            "client_id":     SSO_CLIENT_ID,
            "response_type": "code",
            "redirect_uri":  GRAPH_REDIRECT_URI,
            "response_mode": "query",
            "scope":         GRAPH_SCOPES,
            "state":         state,
        })
        auth_url = (
            f"https://login.microsoftonline.com/{tenant_id}"
            f"/oauth2/v2.0/authorize?{params}"
        )
        self.send_response(302)
        self.send_header("Location", auth_url)
        self._cors_headers()
        self.end_headers()

    def _handle_graph_callback(self):
        qs    = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code  = qs.get("code",  [None])[0]
        state = qs.get("state", [None])[0]
        error = qs.get("error", [None])[0]

        if error:
            self._error(401, f"Graph auth error: {qs.get('error_description', [error])[0]}")
            return
        if not _graph_pending.pop(state, False) or not code:
            self._error(400, "Invalid Graph OAuth callback — state mismatch or missing code")
            return

        tenant_id = _get_effective_tenant_id()
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        body = urllib.parse.urlencode({
            "client_id":    SSO_CLIENT_ID,
            "code":         code,
            "redirect_uri": GRAPH_REDIRECT_URI,
            "grant_type":   "authorization_code",
            "scope":        GRAPH_SCOPES,
        }).encode()
        try:
            req = urllib.request.Request(
                token_url, data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            self._error(500, f"Graph token exchange failed: {e}")
            return

        with _graph_token_lock:
            _graph_token["access_token"]  = data.get("access_token", "")
            _graph_token["refresh_token"] = data.get("refresh_token", "")
            _graph_token["expires_at"]    = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + data.get("expires_in", 3600))
            )
            _graph_token["email"] = _email_from_jwt(_graph_token["access_token"])

        log.info("Graph token stored for %s", _graph_token.get("email"))

        # Close the popup and notify the opener
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(
            b"<!DOCTYPE html><html><body>"
            b"<script>window.opener&&window.opener.postMessage('graph-auth-complete','*');window.close();</script>"
            b"<p>Connected! You can close this window.</p>"
            b"</body></html>"
        )

    def _serve_graph_status(self):
        tenant_id    = _get_effective_tenant_id()
        client_ready = SSO_CLIENT_ID != "FILL_IN_CLIENT_ID"
        if _graph_token.get("access_token") or _graph_token.get("refresh_token"):
            self._json(200, {
                "connected":       True,
                "email":           _graph_token.get("email", ""),
                "valid":           _graph_token_valid(),
                "graphConfigured": True,
            })
        else:
            self._json(200, {
                "connected":       False,
                "graphConfigured": _graph_configured(),
                "tenantDetected":  bool(tenant_id),
                "tenantId":        tenant_id,
                "clientIdNeeded":  not client_ready,
            })

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

    def _test_smtp(self):
        length    = int(self.headers.get("Content-Length", 0))
        body      = json.loads(self.rfile.read(length))
        smtp_host = body.get("smtpHost", "")
        smtp_port = int(body.get("smtpPort", 25))
        smtp_user = body.get("smtpUser", "")
        smtp_pass = body.get("smtpPassword", "")
        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
                smtp.ehlo()
                smtp.starttls()
                code, msg = smtp.ehlo()
                if smtp_user and smtp_pass:
                    smtp.login(smtp_user, smtp_pass)
            self._json(200, {"ok": True, "msg": f"Connected to {smtp_host}:{smtp_port} — STARTTLS + EHLO OK ({code})"})
        except Exception as e:
            self._json(200, {"ok": False, "msg": str(e)})

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
