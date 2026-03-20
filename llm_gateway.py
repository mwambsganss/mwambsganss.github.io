"""llm_gateway.py — Lilly LLM Gateway client.

Requires no third-party libraries beyond the standard library.

Configuration (env vars):
    LLM_GATEWAY_URL     e.g. https://lilly-code-server.api.gateway.llm.lilly.com
    LLM_GATEWAY_KEY     API key (x-api-key header) — takes priority if set
    LLM_MODEL           Model override (default: claude-sonnet-4-20250514-v1)

    OAuth2 fallback (used only when LLM_GATEWAY_KEY is not set):
    LLM_CLIENT_ID       Azure AD application (client) ID
    LLM_CLIENT_SECRET   Azure AD client secret
    LLM_TOKEN_URL       Azure AD token endpoint
                        e.g. https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
    LLM_TOKEN_SCOPE     OAuth2 scope (default: {client_id}/.default)

Usage:
    from llm_gateway import call_llm

    text = call_llm(prompt="Summarise this sprint data...")
    text = call_llm(prompt=..., model="claude-opus-4-6", max_tokens=2048)

Notes:
  - Token is fetched once and cached in-process until 60 s before expiry.
  - Uses a relaxed SSL context (CERT_NONE) for Lilly's corporate CA.
  - Raises LLMError on non-2xx responses.
"""

import json
import logging
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

DEFAULT_MODEL      = "claude-sonnet-4-20250514-v1"
DEFAULT_MAX_TOKENS = 1024
_TOKEN_REFRESH_BUFFER = 60  # seconds before expiry to refresh

# In-process token cache
_cached_token:   str   = ""
_token_expires:  float = 0.0

# Install proxy handler for corporate environments
def _setup_proxy():
    """Configure urllib to use system proxy settings."""
    try:
        from urllib.request import getproxies, ProxyHandler, build_opener, install_opener
        proxies = getproxies()
        if proxies:
            opener = build_opener(ProxyHandler(proxies))
            install_opener(opener)
            log.debug("Proxy handler installed: %s", list(proxies.keys()))
    except Exception as e:
        log.debug("Could not install proxy handler: %s", e)

_setup_proxy()


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
        ctx.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
    return ctx


def _fetch_token(
    token_url:     str,
    client_id:     str,
    client_secret: str,
    scope:         str,
) -> tuple[str, float]:
    """POST to Azure AD token endpoint, return (access_token, expiry_epoch)."""
    body = urllib.parse.urlencode({
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "scope":         scope,
    }).encode()

    req = urllib.request.Request(
        token_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=_ssl_ctx()) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        msg = exc.read().decode()[:300]
        raise LLMError(f"Token fetch HTTP {exc.code}: {msg}") from exc

    token   = data.get("access_token", "")
    expires = time.time() + int(data.get("expires_in", 3600))
    if not token:
        raise LLMError(f"No access_token in response: {json.dumps(data)[:200]}")

    log.debug("OAuth2 token fetched, expires in %ds", data.get("expires_in", 3600))
    return token, expires


def _get_token(
    token_url:     str,
    client_id:     str,
    client_secret: str,
    scope:         str,
) -> str:
    """Return a valid Bearer token, refreshing from Azure AD if needed."""
    global _cached_token, _token_expires
    if _cached_token and time.time() < (_token_expires - _TOKEN_REFRESH_BUFFER):
        return _cached_token
    _cached_token, _token_expires = _fetch_token(token_url, client_id, client_secret, scope)
    return _cached_token


class LLMError(RuntimeError):
    """Raised when the LLM gateway returns a non-2xx response."""


def call_llm(
    prompt:     str,
    url:        str | None = None,
    model:      str | None = None,
    max_tokens: int        = DEFAULT_MAX_TOKENS,
    system:     str | None = None,
    key:        str | None = None,
) -> str:
    """Call the Lilly LLM Gateway and return the assistant's reply text.

    Parameters
    ----------
    prompt:     User message content.
    url:        Gateway base URL (falls back to LLM_GATEWAY_URL env var).
    model:      Model ID (falls back to LLM_MODEL env var, then default).
    max_tokens: Maximum tokens in the response.
    system:     Optional system prompt.
    key:        APIM subscription key (sent as X-LLM-Gateway-Key alongside the
                OAuth2 Bearer token, or as sole auth if OAuth2 env vars are not set).

    Raises
    ------
    LLMError    On HTTP errors or unexpected response shape.
    """
    url   = (url   or os.getenv("LLM_GATEWAY_URL", "")).rstrip("/")
    model = model  or os.getenv("LLM_MODEL", DEFAULT_MODEL)

    if not url:
        raise LLMError("LLM_GATEWAY_URL must be set")

    # Resolve auth — OAuth2 Bearer token + APIM subscription key sent together
    apim_key      = key or os.getenv("LLM_GATEWAY_KEY", "")
    client_id     = os.getenv("LLM_CLIENT_ID", "")
    client_secret = os.getenv("LLM_CLIENT_SECRET", "")
    token_url     = os.getenv("LLM_TOKEN_URL", "")

    if client_id and client_secret and token_url:
        scope        = os.getenv("LLM_TOKEN_SCOPE", "api://llm-gateway.lilly.com/.default")
        bearer_token = _get_token(token_url, client_id, client_secret, scope)
        auth_headers = {"Authorization": f"Bearer {bearer_token}"}
        if apim_key:
            auth_headers["X-LLM-Gateway-Key"] = apim_key
    elif apim_key:
        auth_headers = {"Authorization": f"Bearer {apim_key}"}
    else:
        raise LLMError(
            "No LLM auth configured. Set LLM_CLIENT_ID + LLM_CLIENT_SECRET + LLM_TOKEN_URL "
            "(OAuth2), optionally with LLM_GATEWAY_KEY as the APIM subscription key."
        )

    body: dict = {
        "model":      model,
        "max_tokens": max_tokens,
        "messages":   [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    req = urllib.request.Request(
        f"{url}/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            **auth_headers,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=_ssl_ctx()) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        msg = exc.read().decode()[:300]
        raise LLMError(f"HTTP {exc.code}: {msg}") from exc

    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        text = (data.get("content") or [{}])[0].get("text") or data.get("completion", "")
    if not text:
        raise LLMError(f"Unexpected response shape: {json.dumps(data)[:200]}")

    log.info("LLM call succeeded — model=%s tokens_approx=%d", model, len(text) // 4)
    return text
