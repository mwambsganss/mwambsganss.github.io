#!/usr/bin/env python3
"""Local dev server for Jira Executive Dashboard.

Serves static files and provides:
  GET  /api/auth-token  — returns current user's access token
  GET  /api/login       — starts Lilly SSO (Azure AD) OAuth2 flow
  GET  /api/callback    — handles OAuth2 redirect, stores session
  POST /api/jira-proxy  — server-side proxy for Jira REST API (bypasses CORS)
  POST /api/llm-proxy   — server-side proxy for LLM Gateway (bypasses CORS)
"""
import base64
import http.server
import json
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import ssl
from pathlib import Path

PORT = 8080
SERVE_DIR = Path(__file__).parent

# ── Lilly SSO / Azure AD config ───────────────────────────────────────────────
# To enable browser-based SSO for shared/hosted deployments:
#   1. Register an app in Azure AD (portal.azure.com → App registrations)
#   2. Add redirect URI: http://<your-host>/api/callback
#   3. Fill in the values below
SSO_TENANT_ID    = "FILL_IN_LILLY_TENANT_ID"   # Azure AD tenant ID
SSO_CLIENT_ID    = "FILL_IN_CLIENT_ID"          # App (client) ID
SSO_REDIRECT_URI = f"http://localhost:{PORT}/api/callback"
SSO_SCOPES       = "openid profile email offline_access"
SSO_CONFIGURED   = SSO_TENANT_ID != "FILL_IN_LILLY_TENANT_ID"

# In-memory session store (resets on server restart)
_sessions: dict = {}  # session_id  → {access_token, email, expires_at}
_pending:  dict = {}  # oauth_state → session_id  (CSRF guard)
_keychain: dict = {}  # cached keychain token so macOS only prompts once


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    # ── Routing ───────────────────────────────────────────────────────────────

    def do_POST(self):
        if self.path == "/api/jira-proxy":
            self._proxy_jira()
        elif self.path == "/api/llm-proxy":
            self._proxy_llm()
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
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ── SSO / Auth ────────────────────────────────────────────────────────────

    def _start_sso_login(self):
        if not SSO_CONFIGURED:
            self._error(501, "SSO not configured — fill in SSO_TENANT_ID and SSO_CLIENT_ID in server.py")
            return
        state = secrets.token_urlsafe(16)
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

        # Exchange authorisation code for access token
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
        email        = self._email_from_jwt(access_token)

        _sessions[session_id] = {
            "access_token": access_token,
            "email":        email,
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
        # 1. Check for an active SSO session cookie
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

        # 2. Fallback: macOS keychain token from `lilly-code login`
        # Cache the result so macOS only prompts once per server session
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
            email      = self._email_from_jwt(token)
            self._json(200, {"token": token, "expires_at": expires_at, "email": email})
        except subprocess.CalledProcessError:
            if SSO_CONFIGURED:
                self._json(401, {"error": "Not authenticated", "login_url": "/api/login"})
            else:
                self._error(401, "Not authenticated — run: lilly-code login")
        except Exception as e:
            self._error(500, str(e))

    # ── Proxies ───────────────────────────────────────────────────────────────

    def _serve_llm_models(self):
        """Fetch available models from the LLM gateway's /v1/models endpoint."""
        qs    = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        token = qs.get("token", [None])[0] or ""
        url   = qs.get("url",   ["https://lilly-code-server.api.gateway.llm.lilly.com"])[0]
        target = url.rstrip("/") + "/v1/models"
        req = urllib.request.Request(
            target,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        ctx = self._ssl_ctx()
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = json.loads(resp.read())
            # Anthropic /v1/models returns {"data": [{id, ...}, ...]}
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
    def _ssl_ctx():
        """Unverified SSL context for corporate internal hosts."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode    = ssl.CERT_NONE
        # Python 3.12 / OpenSSL 3.0: suppress abrupt EOF during TLS handshake
        # (common with corporate proxies that intercept TLS)
        if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
            ctx.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
        return ctx

    @staticmethod
    def _email_from_jwt(token: str) -> str:
        parts = token.split(".")
        if len(parts) < 2:
            return ""
        try:
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
            return (
                payload.get("preferred_username")
                or payload.get("upn")
                or payload.get("email")
                or ""
            )
        except Exception:
            return ""

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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
    print(f"Dashboard → http://localhost:{PORT}/dashboard.html")
    if SSO_CONFIGURED:
        print(f"  SSO enabled  — sign in at http://localhost:{PORT}/api/login")
    else:
        print("  SSO not configured — using lilly-code keychain fallback")
        print("  To enable SSO: fill in SSO_TENANT_ID and SSO_CLIENT_ID in server.py")
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
