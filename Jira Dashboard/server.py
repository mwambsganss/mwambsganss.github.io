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
