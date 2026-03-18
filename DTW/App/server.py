#!/usr/bin/env python3
"""Design Thinking Workshop App — Backend Server

Serves the DTW collaborative workshop app with:
  GET    /                              — serve index.html
  GET    /style.css, /app.js            — static assets
  GET    /exercises.json                — exercise catalog
  POST   /api/sessions                  — create session
  GET    /api/sessions                  — list all sessions
  GET    /api/sessions/<id>             — get session state
  POST   /api/sessions/<id>/advance     — next exercise
  POST   /api/sessions/<id>/back        — previous exercise
  POST   /api/sessions/<id>/summary     — generate AI summary
  GET    /api/sessions/<id>/export      — download session JSON

SocketIO events:
  Client→Server:   join_session, send_message, facilitator_join
  Server→Client:   session_state, new_message, exercise_changed,
                   summary_ready, participant_joined, error
"""
import json
import logging
import os
import ssl
import subprocess
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── Load .env (no third-party library needed) ──────────────────────────────────
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room

# ── Config ─────────────────────────────────────────────────────────────────────
PORT       = int(os.environ.get("PORT", 5001))
BASE_DIR   = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger("dtw")

app = Flask(__name__, static_folder=str(BASE_DIR))
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# In-memory map: room_code → session_id  (rebuilt from disk on startup)
_room_code_map: dict[str, str] = {}


# ── Utilities ──────────────────────────────────────────────────────────────────

def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def room_code_from_id(session_id: str) -> str:
    return session_id.replace("-", "")[:6].upper()


def session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"session_{session_id}.json"


def load_session(session_id: str) -> dict | None:
    p = session_path(session_id)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_session(session: dict) -> None:
    p = session_path(session["session_id"])
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
    tmp.replace(p)


def load_exercises() -> list[dict]:
    p = BASE_DIR / "exercises.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def get_exercise_meta(exercise_id: str) -> dict | None:
    for ex in load_exercises():
        if ex["id"] == exercise_id:
            return ex
    return None



def _rebuild_room_code_map() -> None:
    """Rebuild in-memory room_code→session_id map from disk at startup."""
    for p in SESSIONS_DIR.glob("session_*.json"):
        try:
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            rc = s.get("room_code") or room_code_from_id(s["session_id"])
            _room_code_map[rc] = s["session_id"]
        except Exception:
            pass


_rebuild_room_code_map()


# ── AI Summary (Lilly LLM Gateway) ────────────────────────────────────────────

LLM_GATEWAY_URL = os.environ.get(
    "LLM_GATEWAY_URL",
    "https://lilly-code-server.api.gateway.llm.lilly.com"
).rstrip("/")
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")

# ── Facilitator access control ────────────────────────────────────────────────

# Names exactly as they appear in the JWT 'name' claim (case-insensitive match)
FACILITATORS: list[str] = [
    "Matt Wambsganss",
]


_keychain: dict = {}


def _read_keychain_token() -> str:
    """Read the lilly-code JWT from the macOS keychain (populated by Lilly Code VS Code extension).
    The keychain value is a JSON blob: {"access_token": "eyJ...", "expires_at": "..."}.
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "lilly-code", "-w"],
            capture_output=True, text=True, check=True,
        )
        raw = result.stdout.strip()
        try:
            data = json.loads(raw)
            token = data.get("access_token", "")
        except json.JSONDecodeError:
            token = raw  # fallback: treat raw value as the token
        _keychain["token"] = token
        return token
    except subprocess.CalledProcessError:
        log.warning("lilly-code keychain entry not found — AI summaries will fail until you sign in via VS Code")
        return ""


def _decode_jwt_payload(token: str) -> dict:
    """Decode the payload of a JWT without signature verification."""
    import base64
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        # Add padding
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
    except Exception:
        return {}


def _identity_from_keychain() -> dict:
    """Return {name, email, is_facilitator} from the keychain JWT, or empty strings."""
    token = _keychain.get("token", "") or _read_keychain_token()
    if not token:
        return {"name": "", "email": "", "is_facilitator": False}
    claims = _decode_jwt_payload(token)
    name  = claims.get("name") or claims.get("given_name", "")
    email = claims.get("upn") or claims.get("email") or claims.get("preferred_username", "")
    is_fac = name.lower() in [f.lower() for f in FACILITATORS]
    return {"name": name, "email": email, "is_facilitator": is_fac}


def _get_llm_token() -> str:
    """Return a valid gateway token, refreshing from keychain if needed."""
    token = _keychain.get("token", "")
    if not token:
        token = _read_keychain_token()
    return token

def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def generate_exercise_summary(exercise_meta: dict, messages: list[dict]) -> str:
    token = _get_llm_token()
    if not token:
        raise ValueError(
            "No LLM gateway token found. Sign in via the Lilly Code VS Code extension to populate the keychain."
        )

    transcript_lines = []
    for m in messages:
        ts = m.get("timestamp", "")[:16].replace("T", " ")
        transcript_lines.append(f"[{ts}] {m.get('sender','?')}: {m.get('text','')}")
    transcript = "\n".join(transcript_lines) if transcript_lines else "(no messages)"

    participant_names = list({m.get("sender", "?") for m in messages})
    participant_count = len(participant_names)

    system_prompt = (
        "You are an expert Design Thinking Workshop facilitator and synthesizer. "
        "Generate structured summaries of workshop exercise discussions. "
        "Summaries must be actionable, organized, and faithful to what participants actually said. "
        "Always ground your summary in the transcript — do not invent content. "
        "Format your response in clean Markdown with headers and bullet points."
    )

    user_prompt = f"""## Workshop Exercise: {exercise_meta['name']}
**Phase {exercise_meta['phase']} — {exercise_meta['phase_name']}**
**Purpose:** {exercise_meta['description']}
**Desired Outcome:** {exercise_meta['desired_outcome']}

## Participant Discussion Transcript
({len(messages)} messages from {participant_count} participant{'s' if participant_count != 1 else ''}: {', '.join(participant_names)})

{transcript}

## Your Synthesis Task
{exercise_meta['prompt_hint']}

## Required Output Format
Generate a structured summary using this exact structure:

### Key Themes
- (2–4 bullet points capturing the dominant themes in the discussion)

### Exercise Findings
- (Organized findings specific to this exercise type — e.g. Hopes/Fears, Personas, Process Steps, Ideas, etc.)

### Notable Quotes
- "[quote or close paraphrase]" — SenderName
- (2–3 quotes that best capture the spirit of the discussion)

### Key Takeaways
1. (Actionable takeaway — carry this forward)
2. (Actionable takeaway — carry this forward)
3. (Actionable takeaway — carry this forward)

Keep the summary readable in under 2 minutes. Be specific — reference actual content from the transcript."""

    # Combine system + user into a single user message (gateway pattern)
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    payload = json.dumps({
        "model":      LLM_MODEL,
        "max_tokens": 1500,
        "messages":   [{"role": "user", "content": combined_prompt}],
    }).encode()

    req = urllib.request.Request(
        LLM_GATEWAY_URL + "/v1/messages",
        data=payload,
        headers={
            "Authorization":      f"Bearer {token}",
            "Content-Type":       "application/json",
            "anthropic-version":  "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=_ssl_ctx()) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        # If 401/403, the token may have expired — clear it so next call re-reads from keychain
        if e.code in (401, 403):
            _keychain.pop("token", None)
        log.error("LLM Gateway HTTP %s: %s", e.code, body[:500])
        raise RuntimeError(f"LLM Gateway returned {e.code}: {body[:200]}") from e

    return data.get("content", [{}])[0].get("text", "")


# ── HTTP Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(BASE_DIR), filename)


@app.route("/api/sessions", methods=["POST"])
def create_session():
    body = request.json or {}
    session_name = (body.get("session_name") or "").strip()
    exercise_order = body.get("exercise_order") or []

    if not session_name:
        return jsonify({"error": "session_name is required"}), 400
    if not exercise_order:
        return jsonify({"error": "exercise_order must not be empty"}), 400

    session_id = str(uuid.uuid4())
    room_code  = room_code_from_id(session_id)

    # Ensure room code uniqueness (collision is astronomically unlikely but handle it)
    attempts = 0
    while room_code in _room_code_map and attempts < 10:
        session_id = str(uuid.uuid4())
        room_code  = room_code_from_id(session_id)
        attempts  += 1

    # Build exercise state entries
    exercises_state: dict = {}
    for ex_id in exercise_order:
        exercises_state[ex_id] = {
            "messages": [],
            "summary": None,
            "summary_generated_at": None,
            "status": "pending",
        }

    session = {
        "session_id": session_id,
        "session_name": session_name,
        "room_code": room_code,
        "created_at": utcnow(),
        "exercise_order": exercise_order,
        "current_exercise_index": 0,
        "status": "active",
        "participants": [],
        "exercises": exercises_state,
    }

    save_session(session)
    _room_code_map[room_code] = session_id

    log.info("Created session %s (room %s) — %d exercises", session_id, room_code, len(exercise_order))
    return jsonify({"session_id": session_id, "room_code": room_code}), 201


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    sessions = []
    for p in sorted(SESSIONS_DIR.glob("session_*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            sessions.append({
                "session_id": s["session_id"],
                "session_name": s["session_name"],
                "room_code": s["room_code"],
                "created_at": s["created_at"],
                "status": s["status"],
                "participant_count": len(s.get("participants", [])),
                "exercise_count": len(s.get("exercise_order", [])),
                "current_exercise_index": s.get("current_exercise_index", 0),
            })
        except Exception:
            pass
    return jsonify(sessions)


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    # Allow lookup by room code too
    if len(session_id) == 6 and session_id.upper() in _room_code_map:
        session_id = _room_code_map[session_id.upper()]
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    # Strip passcode from response
    safe = {k: v for k, v in s.items() if k != "passcode"}
    return jsonify(safe)


@app.route("/api/sessions/<session_id>/advance", methods=["POST"])
def advance_exercise(session_id):
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    idx = s["current_exercise_index"]
    max_idx = len(s["exercise_order"]) - 1
    if idx >= max_idx:
        return jsonify({"error": "Already at last exercise"}), 400

    s["current_exercise_index"] = idx + 1
    # Mark previous exercise complete
    prev_ex_id = s["exercise_order"][idx]
    s["exercises"][prev_ex_id]["status"] = "completed"
    # Mark new exercise active
    new_ex_id = s["exercise_order"][idx + 1]
    s["exercises"][new_ex_id]["status"] = "active"

    save_session(s)

    ex_meta = get_exercise_meta(new_ex_id) or {}
    socketio.emit("exercise_changed", {
        "exercise_id": new_ex_id,
        "index": idx + 1,
        "exercise_meta": ex_meta,
    }, room=session_id)

    log.info("Session %s advanced to exercise %d (%s)", session_id, idx + 1, new_ex_id)
    return jsonify({"current_exercise_index": idx + 1, "exercise_id": new_ex_id})


@app.route("/api/sessions/<session_id>/back", methods=["POST"])
def back_exercise(session_id):
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    idx = s["current_exercise_index"]
    if idx <= 0:
        return jsonify({"error": "Already at first exercise"}), 400

    s["current_exercise_index"] = idx - 1
    prev_ex_id = s["exercise_order"][idx]
    s["exercises"][prev_ex_id]["status"] = "pending"
    new_ex_id  = s["exercise_order"][idx - 1]
    s["exercises"][new_ex_id]["status"] = "active"

    save_session(s)

    ex_meta = get_exercise_meta(new_ex_id) or {}
    socketio.emit("exercise_changed", {
        "exercise_id": new_ex_id,
        "index": idx - 1,
        "exercise_meta": ex_meta,
    }, room=session_id)

    return jsonify({"current_exercise_index": idx - 1, "exercise_id": new_ex_id})


@app.route("/api/sessions/<session_id>/exercises", methods=["PUT"])
def update_exercises(session_id):
    """Replace the exercise order for a session, preserving existing messages/summaries."""
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    body = request.json or {}
    new_order = body.get("exercise_order") or []
    if not new_order:
        return jsonify({"error": "exercise_order must not be empty"}), 400

    # Preserve existing exercise state; initialise any new exercises
    existing = s.get("exercises", {})
    new_exercises: dict = {}
    for ex_id in new_order:
        new_exercises[ex_id] = existing.get(ex_id, {
            "messages": [], "summary": None, "summary_generated_at": None, "status": "pending",
        })

    # Clamp current_exercise_index to valid range
    new_idx = min(s.get("current_exercise_index", 0), len(new_order) - 1)

    s["exercise_order"] = new_order
    s["exercises"] = new_exercises
    s["current_exercise_index"] = new_idx
    save_session(s)

    # Notify all connected clients
    safe = {k: v for k, v in s.items() if k != "passcode"}
    socketio.emit("session_state", safe, room=session_id)

    log.info("Updated exercise list for session %s (%d exercises)", session_id, len(new_order))
    return jsonify({"exercise_order": new_order, "current_exercise_index": new_idx})


@app.route("/api/sessions/<session_id>/summary", methods=["POST"])
def generate_summary(session_id):
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    idx    = s["current_exercise_index"]
    ex_id  = s["exercise_order"][idx]
    ex_state = s["exercises"].get(ex_id, {})
    messages = ex_state.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages in current exercise to summarize"}), 400

    ex_meta = get_exercise_meta(ex_id)
    if not ex_meta:
        return jsonify({"error": f"Exercise metadata not found for '{ex_id}'"}), 500

    try:
        summary_text = generate_exercise_summary(ex_meta, messages)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log.error("Summary generation failed: %s", e)
        return jsonify({"error": f"AI summary failed: {e}"}), 500

    s["exercises"][ex_id]["summary"] = summary_text
    s["exercises"][ex_id]["summary_generated_at"] = utcnow()
    save_session(s)

    socketio.emit("summary_ready", {
        "exercise_id": ex_id,
        "summary_text": summary_text,
    }, room=session_id)

    log.info("Summary generated for session %s exercise %s", session_id, ex_id)
    return jsonify({"exercise_id": ex_id, "summary_text": summary_text})


@app.route("/api/config")
def get_config():
    """Return public Azure AD config for frontend MSAL.js auth."""
    return jsonify({
        "azure_client_id": os.environ.get("AZURE_CLIENT_ID", ""),
        "azure_tenant_id": os.environ.get("AZURE_TENANT_ID", ""),
    })


@app.route("/api/me")
def get_me():
    """Return current user identity decoded from the keychain JWT."""
    identity = _identity_from_keychain()
    return jsonify(identity)


@app.route("/api/facilitator-auth", methods=["POST"])
def facilitator_auth():
    """Authenticate a facilitator by name (fallback when keychain unavailable)."""
    body = request.json or {}
    name = (body.get("name") or "").strip()

    if name.lower() not in [f.lower() for f in FACILITATORS]:
        return jsonify({"error": "Name not on facilitator list"}), 403

    return jsonify({"name": name, "is_facilitator": True})


@app.route("/api/sessions/<session_id>/export", methods=["GET"])
def export_session(session_id):
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    safe_name = s["session_name"].replace(" ", "_")[:40]
    filename  = f"DTW_{safe_name}_{session_id[:8]}.json"
    resp = app.response_class(
        response=json.dumps(s, indent=2, ensure_ascii=False),
        status=200,
        mimetype="application/json",
    )
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# ── SocketIO Events ────────────────────────────────────────────────────────────

@socketio.on("join_session")
def handle_join(data):
    session_id   = data.get("session_id", "").strip()
    display_name = (data.get("display_name") or "").strip()

    # Allow room code lookup
    if len(session_id) == 6 and session_id.upper() in _room_code_map:
        session_id = _room_code_map[session_id.upper()]

    s = load_session(session_id)
    if not s:
        emit("error", {"message": "Session not found. Check your room code."})
        return

    if not display_name:
        emit("error", {"message": "Display name is required."})
        return

    join_room(session_id)

    # Add participant if new
    existing = [p["name"] for p in s.get("participants", [])]
    if display_name not in existing:
        s["participants"].append({"name": display_name, "joined_at": utcnow()})
        save_session(s)
        socketio.emit("participant_joined", {"name": display_name}, room=session_id)
        log.info("Participant '%s' joined session %s", display_name, session_id)

    # Send full session state to this client
    safe = {k: v for k, v in s.items() if k != "passcode"}
    emit("session_state", safe)


@socketio.on("facilitator_join")
def handle_facilitator_join(data):
    session_id = data.get("session_id", "").strip()

    s = load_session(session_id)
    if not s:
        emit("error", {"message": "Session not found."})
        return

    join_room(session_id)
    safe = {k: v for k, v in s.items() if k != "passcode"}
    emit("session_state", safe)
    log.info("Facilitator joined session %s", session_id)


@socketio.on("send_message")
def handle_message(data):
    session_id = data.get("session_id", "").strip()
    sender     = (data.get("sender") or "").strip()
    text       = (data.get("text") or "").strip()
    exercise_id = (data.get("exercise_id") or "").strip()

    if not session_id or not sender or not text:
        emit("error", {"message": "Missing required fields."})
        return

    s = load_session(session_id)
    if not s:
        emit("error", {"message": "Session not found."})
        return

    msg = {
        "sender":      sender,
        "timestamp":   utcnow(),
        "text":        text,
        "exercise_id": exercise_id,
    }

    # Store under the correct exercise
    if exercise_id and exercise_id in s["exercises"]:
        s["exercises"][exercise_id]["messages"].append(msg)
    else:
        # Fallback: store under current exercise
        idx    = s["current_exercise_index"]
        ex_id  = s["exercise_order"][idx] if s["exercise_order"] else None
        if ex_id and ex_id in s["exercises"]:
            msg["exercise_id"] = ex_id
            s["exercises"][ex_id]["messages"].append(msg)

    save_session(s)
    socketio.emit("new_message", msg, room=session_id)


# ── Startup ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("DTW Workshop App starting on http://localhost:%d", PORT)
    log.info("Sessions directory: %s", SESSIONS_DIR)
    token = _read_keychain_token()
    if token:
        log.info("LLM Gateway configured: %s (model: %s) ✓", LLM_GATEWAY_URL, LLM_MODEL)
    else:
        log.warning("lilly-code keychain token not found — AI summaries disabled until you sign in via VS Code")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False)
