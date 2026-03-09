#!/usr/bin/env python3
"""Local dev server for Jira Executive Dashboard.

Serves static files and provides a /api/auth-token endpoint that reads the
current lilly-code access token from the macOS keychain so the dashboard can
use it without the user manually pasting credentials.
"""
import http.server
import json
import subprocess
from pathlib import Path

PORT = 8080
SERVE_DIR = Path(__file__).parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/jira-proxy":
            self._proxy_jira()
        elif self.path == "/api/llm-proxy":
            self._proxy_llm()
        else:
            self._error(404, "Not found")

    def _proxy_jira(self):
        import urllib.request, urllib.error, ssl
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        target_url = body.get("url", "")
        headers = body.get("headers", {})
        req = urllib.request.Request(target_url, headers=headers)
        # Use an unverified SSL context for corporate internal Jira instances
        # whose cert chain may not be in Python's default CA bundle
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self._error(e.code, e.read().decode()[:300])
        except Exception as e:
            self._error(500, str(e))

    def _proxy_llm(self):
        import urllib.request, urllib.error, ssl
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        target_url = body.get("url", "")
        req_headers = body.get("headers", {})
        req_body = json.dumps(body.get("body", {})).encode()
        req = urllib.request.Request(target_url, data=req_body, headers=req_headers, method="POST")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except urllib.error.HTTPError as e:
            self._error(e.code, e.read().decode()[:500])
        except Exception as e:
            self._error(500, str(e))

    def do_GET(self):
        if self.path == "/api/auth-token":
            self._serve_auth_token()
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _serve_auth_token(self):
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "lilly-code", "-w"],
                capture_output=True, text=True, check=True,
            )
            data = json.loads(result.stdout.strip())
            token = data.get("access_token", "")
            expires_at = data.get("expires_at", "")
            # Decode email from JWT payload (no verification needed — local use)
            import base64
            parts = token.split(".")
            email = ""
            if len(parts) >= 2:
                payload = parts[1] + "=="  # pad
                try:
                    decoded = json.loads(base64.urlsafe_b64decode(payload))
                    email = decoded.get("preferred_username", "")
                except Exception:
                    pass
            body = json.dumps({"token": token, "expires_at": expires_at, "email": email})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(body.encode())
        except subprocess.CalledProcessError:
            self._error(401, "Not authenticated — run: lilly-code login")
        except Exception as e:
            self._error(500, str(e))

    def _error(self, code, message):
        body = json.dumps({"error": message})
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, fmt, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    print(f"Dashboard → http://localhost:{PORT}/dashboard.html")
    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
