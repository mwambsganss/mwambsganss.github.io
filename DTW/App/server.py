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
  GET    /api/sessions/<id>/export-chat — download full chat log as .docx

SocketIO events:
  Client→Server:   join_session, send_message, facilitator_join
  Server→Client:   session_state, new_message, exercise_changed,
                   summary_ready, participant_joined, error
"""
import io
import json
import logging
import os
import ssl
import subprocess
import sys
import tempfile
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
import eventlet.tpool
eventlet.monkey_patch()

from flask import Flask, jsonify, request, send_from_directory, Response
from flask_socketio import SocketIO, emit, join_room

# ── Config ─────────────────────────────────────────────────────────────────────
PORT       = int(os.environ.get("PORT", 5001))
BASE_DIR   = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

# ── S3 storage (optional — falls back to local filesystem when not configured) ──
S3_BUCKET  = os.environ.get("S3_BUCKET", "")           # e.g. "lilly-dtw-sessions"
S3_REGION  = os.environ.get("S3_REGION", "us-east-1")
S3_PREFIX  = os.environ.get("S3_PREFIX", "dtw")        # key prefix inside bucket
# Credentials are picked up automatically from:
#   AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY env vars, ~/.aws/credentials, or IAM role
_S3_CLIENT = None  # initialised lazily on first use


def _s3():
    """Return a boto3 S3 client, creating it on first call."""
    global _S3_CLIENT
    if _S3_CLIENT is None:
        import boto3
        _S3_CLIENT = boto3.client("s3", region_name=S3_REGION)
    return _S3_CLIENT


def _s3_enabled() -> bool:
    return bool(S3_BUCKET)

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


def _s3_session_key(session_id: str) -> str:
    return f"{S3_PREFIX}/sessions/session_{session_id}.json"


def load_session(session_id: str) -> dict | None:
    if _s3_enabled():
        try:
            obj = _s3().get_object(Bucket=S3_BUCKET, Key=_s3_session_key(session_id))
            return json.loads(obj["Body"].read().decode("utf-8"))
        except Exception:
            return None
    p = session_path(session_id)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_session(session: dict) -> None:
    body = json.dumps(session, indent=2, ensure_ascii=False).encode("utf-8")
    if _s3_enabled():
        _s3().put_object(
            Bucket=S3_BUCKET,
            Key=_s3_session_key(session["session_id"]),
            Body=body,
            ContentType="application/json",
        )
        return
    p = session_path(session["session_id"])
    tmp = p.with_suffix(".tmp")
    tmp.write_bytes(body)
    tmp.replace(p)


def _rebuild_room_code_map() -> None:
    """Rebuild in-memory room_code→session_id map from storage at startup."""
    if _s3_enabled():
        try:
            paginator = _s3().get_paginator("list_objects_v2")
            prefix = f"{S3_PREFIX}/sessions/"
            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
                for obj in page.get("Contents", []):
                    try:
                        raw = _s3().get_object(Bucket=S3_BUCKET, Key=obj["Key"])
                        s = json.loads(raw["Body"].read().decode("utf-8"))
                        rc = s.get("room_code") or room_code_from_id(s["session_id"])
                        _room_code_map[rc] = s["session_id"]
                    except Exception:
                        pass
        except Exception as exc:
            log.warning("Could not rebuild room code map from S3: %s", exc)
        return
    for p in SESSIONS_DIR.glob("session_*.json"):
        try:
            with open(p, encoding="utf-8") as f:
                s = json.load(f)
            rc = s.get("room_code") or room_code_from_id(s["session_id"])
            _room_code_map[rc] = s["session_id"]
        except Exception:
            pass


_rebuild_room_code_map()


def load_exercises() -> list[dict]:
    p = BASE_DIR / "exercises.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def get_exercise_meta(exercise_id: str) -> dict | None:
    for ex in load_exercises():
        if ex["id"] == exercise_id:
            return ex
    return None


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
    """Return a valid gateway token, always re-reading from keychain so a VS Code re-login is picked up immediately."""
    return _read_keychain_token()

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
        "You are an expert Design Thinking Workshop facilitator trained in IBM Enterprise Design Thinking methodology. "
        "Your role is to synthesize live workshop discussions into structured, executive-ready outputs. "
        "Outputs should be actionable, specific, and grounded entirely in what participants actually said — never invent content. "
        "Format responses in clean Markdown. Use ## for section headers and - for bullets. "
        "Each section header becomes a slide in the deliverable deck, so keep headers short and descriptive. "
        "Write as if preparing a professional workshop output that will be shared with senior leadership."
    )

    # Exercise-specific output structure mapped to IBM field guide methodology
    output_formats = {
        "intros_outcomes": """## Output Structure
## Participants in the Room
-- (Name and role/team for each participant who introduced themselves)

## Desired Outcomes
-- (Summarized outcomes — synthesize participant input into clear, concise statements; do not quote verbatim)

## Common Themes
-- (2–3 themes that emerged across multiple desired outcomes)

## Shared Definition of Success
-- (1–2 sentences capturing what the group collectively wants to achieve today)""",

        "hopes_fears": """## Output Structure
## Hopes
- (Each hope, close to participant's own words — organized by theme)

## Fears
- (Each fear or concern, close to participant's own words — organized by theme)

## Key Tensions
- (Hopes and fears that are in direct conflict with each other)

## Implications for the Workshop
- (How should the facilitator use these to shape the day)""",

        "persona_cards": """## Output Structure
For each distinct persona mentioned, create a section:

## Persona: [Role Title]
- **Goals:** what they are trying to accomplish
- **Pain Points:** top 2–3 frustrations
- **Representative Quote:** one quote that captures their experience

Repeat for each persona. End with:

## Common Threads Across Personas
- (Shared goals or frustrations that span multiple roles)""",

        "stakeholder_map": """## Output Structure
## Core Process Owners
- (Roles who own steps in the process — executors)

## Decision Makers
- (Roles who approve, gate, or direct the work)

## Impacted Parties
- (Roles who feel the downstream effects but don't control the process)

## Enablers & Support Roles
- (Roles that provide tools, data, or support but aren't in the critical path)

## Key Friction Points
- (Where stakeholder relationships are unclear or cause conflict)""",

        "empathy_maps": """## Output Structure
Create ONE section per persona. Use EXACTLY this format for each:

## [Persona Name / Role]
- **SAYS:** "[A direct quote or paraphrase of something this persona says aloud]"
- **SAYS:** "[Another representative quote]"
- **DOES:** [A concrete action or behavior they perform in the process]
- **DOES:** [Another action or behavior]
- **THINKS:** [An internal assumption, mental model, or belief they hold]
- **THINKS:** [Another thought or concern they rarely voice]
- **FEELS:** [An emotional state — frustration, anxiety, pride, confusion]
- **FEELS:** [Another emotion or tension they experience]

Repeat the ## [Persona Name / Role] block for every persona identified in the conversation.
End with:

## Common Threads Across Personas
- (Shared pain points, emotions, or beliefs that span multiple personas)""",

        "asis_process_map": """## Output Structure
## Process Overview
- (Brief description of the process being mapped and key roles involved)

## Process Steps
- **Step 1 — [Step Name]:** Owner: [Role]. What happens. Pain points if any.
- (Continue for each step in sequence)

## Key Handoff Points
- (Where work moves between teams — flag delays or confusion here)

## Pain Points by Stage
- (Grouped frustrations: where does the most friction occur and why)

## Root Cause Patterns
- (Structural issues: parallel execution, ownership fragmentation, communication gaps)""",

        "needs_statements": """## Output Structure
## Formal Needs Statements
- [Persona] needs a way to [action] so that [benefit].
- (One statement per line — restate participant input in this exact format)

## Needs Grouped by Theme
### [Theme Name]
- (Related needs that address the same underlying problem)

## Highest-Priority Needs
- (Top 3 needs most cited or most impactful — these should anchor the ideation phase)""",

        "assumptions_grid": """## Output Structure
## High-Risk / Uncertain — Must Validate First
- (Assumptions or questions that are both high-stakes and unproven)

## High-Risk / Certain — Monitor Closely
- (Known facts that are high-stakes — ensure team stays aligned)

## Low-Risk / Uncertain — Worth Exploring
- (Open questions that are good to answer but not blocking)

## Top 3 Most Pressing Unknowns
1. [Unknown] — Why it matters / what to do to validate it
2. [Unknown] — Why it matters / what to do to validate it
3. [Unknown] — Why it matters / what to do to validate it""",

        "big_idea_vignettes": """## Output Structure
Group ideas into 3–5 thematic clusters:

## [Theme: e.g., Automation & AI]
- **[Idea Headline]:** one-sentence description
- (All ideas in this cluster)

## [Theme: e.g., Process Clarity & Ownership]
- **[Idea Headline]:** one-sentence description

(Repeat for each theme)

## Standout Ideas
- (Ideas that appeared more than once or generated notable enthusiasm)

## Ideas for Fast Follow-up
- (Ideas simple enough to act on quickly — quick wins)""",

        "prioritization_grid": """## Output Structure
## No-Brainers — High Importance, High Feasibility
1. [Idea] — why it's both important and achievable
2. (List all no-brainer items — these are immediate priorities)

## Big Bets — High Importance, Lower Feasibility
1. [Idea] — what makes it hard, why it's still worth pursuing
2. (List big bets — these need planning and investment)

## Utilities — Lower Importance, High Feasibility
- [Idea] — worth doing eventually but not the top priority

## Top 5 Prioritized Opportunities
1. [Opportunity name and one-sentence rationale]
2.
3.
4.
5.""",

        "tobe_process_map": """## Output Structure
## Improved Process Overview
- (What fundamentally changes from the As-Is state)

## Future-State Process Steps
- **Step 1 — [Step Name]:** What changes. Which pain points resolved. New capability required.
- (Continue for each step)

## Pain Points Resolved
- (Explicit mapping: old pain point → how the new process addresses it)

## New Capabilities Required
- (What tools, systems, or behaviors must exist for this future state to work)

## Quick Wins vs. Longer-Term Changes
- **Quick Wins:** changes that can be made immediately
- **Longer-term:** changes requiring system or org investment""",

        "experience_roadmap": """## Output Structure
## Near-Term (1–3 months) — Our User Can…
- (Capability statements starting with "Our user can…")

## Mid-Term (4–6 months) — Our User Can…
- (Capability statements starting with "Our user can…")

## Long-Term (7–12 months) — Our User Can…
- (Capability statements starting with "Our user can…")

## What We Will Learn at Each Stage
- Near-term learning: [what validated assumptions will tell us]
- Mid-term learning: [what to measure and refine]""",

        "hills_objectives": """## Output Structure
For each Hill/Objective:

## Objective [N]: [Short Name]
- **Who:** [the specific user this is for]
- **What:** [what they will be able to do that they can't today]
- **Wow:** [measurable outcome that proves success]
- **Pain Addressed:** [which current pain points this resolves]
- **Deliverables:** [concrete outputs required to achieve this Hill]
- **Quantified Value:** [estimated time saved, errors reduced, or experience improved]

(Repeat for each Hill — aim for 2–3 total)""",

        "gantt_roadmap": """## Output Structure
## Short-Term (Months 1–3)
- [Initiative name] — owner, effort level (Low/Med/High), dependencies

## Mid-Term (Months 4–6)
- [Initiative name] — owner, effort level, dependencies

## Long-Term (Months 7–12)
- [Initiative name] — owner, effort level, dependencies

## Dependencies & Sequencing
- (What must happen before what — flag blockers)

## High-Priority Items
- (Initiatives that are blockers for the rest of the roadmap)""",

        "resource_plan": """## Output Structure
## Resource Summary by Initiative
| Initiative | Owner | Skills Required | Effort | Dependencies | Gap? |
|------------|-------|-----------------|--------|--------------|------|
(Fill in each initiative)

## Ownership Gaps — Needs Assignment
- (Initiatives with no clear owner — flag as risks)

## Cross-Team Dependencies
- (Where multiple teams must coordinate — identify the connection point)

## Recommended First Hire or Partnership
- (If resource gaps exist, what role or team should be engaged first)""",

        "feedback_grid": """## Output Structure
## Things That Worked
- (What participants said was effective — keep doing these)

## Things to Change
- (What participants want done differently next time)

## Questions We Still Have
- (Open questions not resolved in the workshop)

## New Ideas to Try
- (Ideas sparked by the workshop that weren't in scope today)

## Top 2–3 Actions from This Feedback
- (Concrete changes to make based on the most-cited feedback items)""",

        "executive_summary": """## Output Structure
## Problem Statement
- (The core challenge this workshop addressed, in 2–3 sentences)

## Key Users
- (Who is affected — roles, teams, and their primary pain)

## Top 3 Insights
1. [Insight — what the team learned that they didn't know before]
2.
3.

## Top Pain Points
- (Most impactful friction points identified across all exercises)

## Top 5 Ideas
1. [Idea and brief rationale]
2.
3.
4.
5.

## Agreed Hills / Objectives
- (The 2–3 Hill statements the team committed to)

## Immediate Next Steps
- [Action] — Owner: [Name], Target: [Date]
- (2–4 concrete next steps with owners)""",

        "playback_deck": """## Output Structure
## Workshop Context & Objectives
- (Why we ran this workshop, what problem we set out to solve)

## Key Personas & Challenges
- (Who is affected and what their core experience looks like today)

## Key Insights from Empathy Work
- (The most important things we learned about how people experience the current state)

## Hills / Success Outcomes
- (The 2–3 Hills the team aligned on — WHO / WHAT / WOW)

## Roadmap Highlights
- (Near-term, mid-term, and long-term milestones)

## Next Steps & Asks
- (What leadership needs to support, decide, or resource)""",
    }

    ex_id = exercise_meta.get("id", "")
    output_format = output_formats.get(ex_id, """## Output Structure
## Key Themes
- (2–4 dominant themes from the discussion)

## Exercise Findings
- (Key findings organized by the exercise's specific framework)

## Notable Quotes
- "[quote]" — SenderName

## Key Takeaways
1. (Actionable takeaway)
2. (Actionable takeaway)
3. (Actionable takeaway)""")

    user_prompt = f"""## Workshop Exercise: {exercise_meta['name']}
**Phase {exercise_meta['phase']} — {exercise_meta['phase_name']}**
**Purpose:** {exercise_meta['description']}
**Desired Outcome:** {exercise_meta['desired_outcome']}

## Participant Discussion Transcript
({len(messages)} messages from {participant_count} participant{'s' if participant_count != 1 else ''}: {', '.join(participant_names)})

{transcript}

## Your Synthesis Task
{exercise_meta['prompt_hint']}

{output_format}

Ground every bullet in the transcript. Be specific — use participant names where it adds value. Write executive-ready prose: concise, direct, no filler. This output becomes the PPTX and DOCX deliverable for this exercise."""

    # Combine system + user into a single user message (gateway pattern)
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"

    payload = json.dumps({
        "model":      LLM_MODEL,
        "max_tokens": 2500,
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


@app.route("/api/sessions/test", methods=["POST"])
def create_test_session():
    """Create a session pre-filled with synthetic participant chats for every exercise."""
    import random

    FAKE_PARTICIPANTS = [
        {"name": "Sarah Chen",       "role": "Digital Marketing Manager"},
        {"name": "Marcus Rodriguez", "role": "Campaign Operations Lead"},
        {"name": "Priya Nair",       "role": "Marketing Analytics Analyst"},
        {"name": "James Okafor",     "role": "Brand Strategy Director"},
        {"name": "Lily Thompson",    "role": "Content & Creative Specialist"},
    ]

    SYNTHETIC_CHATS: dict[str, list[str]] = {
        "intros_outcomes": [
            "Hi everyone — Sarah Chen, Digital Marketing Manager. Today I want to understand where our trafficking process is actually breaking down.",
            "Marcus here — Campaign Ops. My goal is to get clarity on handoff points that cause the most delays.",
            "Priya, analytics. I want to map out where data gets lost between teams and find a way to fix it.",
            "James, Brand Strategy. Hoping we come out of today with prioritized improvements we can actually act on.",
            "Lily from Creative. I want the team to understand what it's like waiting days for feedback on assets.",
        ],
        "hopes_fears": [
            "Hope: We finally agree on a single source of truth for campaign status. Fear: We'll talk a lot but leave without clear owners.",
            "Hope: Identify the 2-3 changes that will have the biggest impact. Fear: Politics get in the way of honest conversation.",
            "Hope: Data quality improves so we can actually trust our reporting. Fear: Any solutions will be too complex to adopt.",
            "Hope: Leadership backs the changes we recommend. Fear: We scope too broadly and try to fix everything at once.",
            "Hope: Creative and ops teams build empathy for each other's constraints. Fear: We don't have enough time to go deep.",
        ],
        "persona_cards": [
            "The Campaign Manager: juggles 15+ campaigns, no single place to check status, constantly chasing updates via Slack.",
            "The Trafficking Specialist: receives briefs at the last minute, unclear specs, spends 40% of time on rework.",
            "The Analytics Lead: waits until campaign end to pull data because mid-flight reporting is unreliable.",
            "The Creative Producer: told 'urgent' so often the word has lost meaning; unclear which feedback is final.",
            "The Brand Director: wants a dashboard but gets a PowerPoint; has to manually reconcile numbers before every Monday review.",
        ],
        "stakeholder_map": [
            "Core owners: Campaign Managers and Trafficking Specialists — they touch every step.",
            "Decision makers: Brand Directors approve final creative and control budget reallocation.",
            "Impacted: Paid Media buyers feel the ripple effect when trafficking is delayed — their optimization windows shrink.",
            "Enablers: Marketing Ops owns the trafficking platform but isn't looped in until things break.",
            "Key friction: Brand and Ops rarely meet — decisions get made in siloes then conflict at handoff.",
        ],
        "empathy_maps": [
            "Campaign Manager SAYS: 'I have no idea where things stand until something breaks.' FEELS: anxious, always reactive.",
            "Trafficking Specialist SAYS: 'I get briefs with missing fields constantly.' DOES: creates unofficial checklists to compensate.",
            "Analytics Lead THINKS: 'If the data were clean we could optimize mid-flight.' FEELS: frustrated by manual reconciliation.",
            "Creative Producer DOES: sends assets to Slack AND email AND the platform because they don't trust any single channel.",
            "Brand Director THINKS: 'Why can't I see real-time campaign status?' SAYS: 'I need a simpler dashboard.' FEELS: out of the loop.",
        ],
        "asis_process_map": [
            "Phase 1 — Brief: Campaign Manager creates brief in Word doc, emails to Creative and Trafficking separately. No version control.",
            "Phase 2 — Creative: Designer picks up brief; average 2.1 rounds of revision due to unclear specs. No structured feedback tool.",
            "Phase 3 — Trafficking: Specialist manually enters specs into platform. 30% error rate requires re-entry.",
            "Phase 4 — QA: QA team reviews against original brief — but brief has often changed by this point.",
            "Phase 5 — Launch: Campaign goes live but Analytics isn't notified; reporting setup is delayed by 2–3 days.",
            "Key pain: Handoff between Creative and Trafficking has no formal step — files are shared via email attachment.",
        ],
        "needs_statements": [
            "Campaign Managers need a way to see real-time trafficking status so they can proactively manage client expectations.",
            "Trafficking Specialists need a way to receive complete, validated briefs so they can reduce re-work.",
            "Analytics team needs a way to access campaign parameters at launch so they can configure tracking without delay.",
            "Creative team needs a way to receive consolidated, final feedback so they can deliver approved assets on first submission.",
            "Brand Directors need a way to monitor campaign health in one view so they can intervene before issues escalate.",
        ],
        "assumptions_grid": [
            "High confidence / High risk: Traffickers are the main source of delays. If wrong, solving trafficking won't move the needle.",
            "High confidence / Low risk: Teams want a unified brief format. Low risk to test — just try it.",
            "Low confidence / High risk: A new platform will solve the coordination problem. Could be expensive and fail.",
            "Low confidence / Low risk: Teams will adopt a new status dashboard without training. Worth piloting cheaply.",
            "Key question: Does leadership actually have time to participate in process redesign, or will this stall?",
        ],
        "big_idea_vignettes": [
            "Idea 1: A single campaign workspace — brief, creative, trafficking, and reporting all in one tool. No more email handoffs.",
            "Idea 2: An AI-powered brief validator that flags incomplete or ambiguous fields before the brief is submitted.",
            "Idea 3: Auto-notify Analytics the moment a campaign goes live, with all parameters pre-populated.",
            "Idea 4: A weekly 15-minute cross-functional sync replacing 40+ status Slack messages. Structured agenda, rotating owner.",
            "Idea 5: Dashboard for Brand Directors — live campaign health score, auto-updated, no manual PowerPoint needed.",
        ],
        "prioritization_grid": [
            "High importance / High feasibility: Standardized brief template — do this first, costs nothing, high impact.",
            "High importance / Low feasibility: Unified campaign platform — high value but requires 12-month procurement.",
            "Low importance / High feasibility: Auto-email status updates — easy win but not the core problem.",
            "Low importance / Low feasibility: AI brief validator — interesting but complex and unproven; revisit in 6 months.",
            "Team consensus: Start with brief template + cross-functional sync. Quick wins before platform change.",
        ],
        "tobe_process_map": [
            "Phase 1 — Brief: Standardized brief form with required fields; auto-validated before submission to Creative.",
            "Phase 2 — Creative: Feedback consolidated in single platform; Creative receives one clear revision round.",
            "Phase 3 — Trafficking: Specs auto-populated from approved brief; manual entry eliminated for standard fields.",
            "Phase 4 — QA: QA checks against the live brief version (not the original email); discrepancies flagged automatically.",
            "Phase 5 — Launch: Analytics auto-notified at launch with all parameters; same-day reporting setup.",
        ],
        "experience_roadmap": [
            "Near-term (0–3 months): 'Our users can submit complete briefs using a shared template.' Launch brief standard + training.",
            "Mid-term (3–9 months): 'Our users can see campaign status in one place without asking.' Build lightweight status tracker.",
            "Long-term (9–18 months): 'Our users can access real-time performance data from day one of launch.' Integrate trafficking + analytics.",
        ],
        "hills_objectives": [
            "Hill 1: Campaign Managers can see trafficking status in real time without sending a single Slack message.",
            "Hill 2: Trafficking Specialists receive zero incomplete briefs by end of Q3.",
            "Hill 3: Analytics is configured and live within 4 hours of campaign launch — not 2 days.",
            "Deliverables: Brief template (immediate), status tracker pilot (Q2), analytics integration spec (Q3).",
            "Quantified value: 30% reduction in rework, 2-day reduction in time-to-launch, 100% same-day analytics.",
        ],
        "gantt_roadmap": [
            "Month 1–2: Design and pilot standardized brief template with 2 campaign managers.",
            "Month 2–3: Roll out brief template org-wide; establish weekly cross-functional sync cadence.",
            "Month 3–6: Build and test lightweight status tracker; integrate with existing trafficking platform.",
            "Month 6–9: Analytics auto-notification pilot; measure time-to-reporting improvement.",
            "Month 9–12: Evaluate unified platform options; RFP if KPIs are met.",
        ],
        "resource_plan": [
            "Owner: Marcus Rodriguez (Campaign Ops Lead) — accountable for brief template and status tracker.",
            "Support: Priya Nair (Analytics) — defines tracking requirements and validates reporting improvements.",
            "Exec sponsor: James Okafor (Brand Strategy Director) — approves budget, removes blockers.",
            "External: May need 1 FTE contractor for platform integration in months 3–9.",
            "Budget estimate: $0 for process changes; $50–80K for status tracker; $200–400K for platform evaluation.",
        ],
        "feedback_grid": [
            "Worked well: The empathy map exercise — teams genuinely understood each other's pain for the first time.",
            "Change: The assumptions grid felt rushed; would benefit from a longer timebox.",
            "New idea: Record a short video summary of the day and share with stakeholders who couldn't attend.",
            "Questions: How do we keep momentum after today? Who owns follow-through on the brief template?",
            "Overall: High energy, honest conversation, clear next steps — best DTW we've run.",
        ],
        "executive_summary": [
            "Core finding: Campaign trafficking delays stem from three root causes — incomplete briefs, fragmented status visibility, and disconnected analytics setup.",
            "Key insight: All personas experience the same process, but from completely different vantage points — alignment was missing, not intent.",
            "Priority 1: Standardized brief template — immediate, zero cost, eliminates 30% of rework.",
            "Priority 2: Live status tracker — 3-month build, eliminates Slack chasing, gives Brand Directors real-time visibility.",
            "Priority 3: Analytics auto-notification at launch — 6-month integration, enables same-day reporting.",
            "Call to action: Approve brief template this week; allocate Q2 budget for status tracker development.",
        ],
        "playback_deck": [
            "We started today asking: why does it take so long to get a campaign live?",
            "We mapped the as-is process and found 5 key friction points — all caused by information gaps, not effort gaps.",
            "We defined what our users need: complete briefs, visible status, same-day analytics.",
            "We prioritized three hills: no Slack chasing, zero incomplete briefs, analytics live in 4 hours.",
            "Our roadmap: brief template now, status tracker in Q2, analytics integration in H2.",
            "Next step: James approves brief template standard by Friday. Marcus leads rollout in 30 days.",
        ],
    }

    # Build all exercises with synthetic messages
    all_ex_ids = [
        "intros_outcomes", "persona_cards", "executive_summary",
        "hopes_fears", "stakeholder_map", "empathy_maps",
        "asis_process_map", "needs_statements", "assumptions_grid",
        "big_idea_vignettes", "prioritization_grid", "tobe_process_map",
        "experience_roadmap", "hills_objectives", "gantt_roadmap",
        "resource_plan", "feedback_grid", "playback_deck",
    ]

    session_id = str(uuid.uuid4())
    room_code  = room_code_from_id(session_id)
    while room_code in _room_code_map:
        session_id = str(uuid.uuid4())
        room_code  = room_code_from_id(session_id)

    exercises_state: dict = {}
    for ex_id in all_ex_ids:
        lines = SYNTHETIC_CHATS.get(ex_id, [])
        messages = []
        for i, text in enumerate(lines):
            participant = FAKE_PARTICIPANTS[i % len(FAKE_PARTICIPANTS)]
            messages.append({
                "sender":    participant["name"],
                "text":      text,
                "timestamp": f"2026-03-18T{10 + i // 60:02d}:{i % 60:02d}:00Z",
                "role":      participant["role"],
            })
        exercises_state[ex_id] = {
            "messages": messages,
            "summary": None,
            "summary_generated_at": None,
            "status": "pending",
        }
    exercises_state[all_ex_ids[0]]["status"] = "active"

    session = {
        "session_id": session_id,
        "session_name": "⚗ Test Session — Synthetic Data",
        "room_code": room_code,
        "created_at": utcnow(),
        "exercise_order": all_ex_ids,
        "current_exercise_index": 0,
        "status": "active",
        "participants": [{"name": p["name"], "role": p["role"], "joined_at": utcnow()} for p in FAKE_PARTICIPANTS],
        "exercises": exercises_state,
    }

    save_session(session)
    _room_code_map[room_code] = session_id
    log.info("Created test session %s (room %s)", session_id, room_code)
    return jsonify({"session_id": session_id, "room_code": room_code}), 201


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    sessions = []
    if _s3_enabled():
        try:
            paginator = _s3().get_paginator("list_objects_v2")
            prefix = f"{S3_PREFIX}/sessions/"
            objs = []
            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
                objs.extend(page.get("Contents", []))
            # Sort by LastModified descending
            objs.sort(key=lambda o: o["LastModified"], reverse=True)
            for obj in objs:
                try:
                    raw = _s3().get_object(Bucket=S3_BUCKET, Key=obj["Key"])
                    s = json.loads(raw["Body"].read().decode("utf-8"))
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
        except Exception as exc:
            log.error("list_sessions S3 error: %s", exc)
    else:
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


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """Delete a session and all its artifacts."""
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    room_code = s.get("room_code", "")

    if _s3_enabled():
        # Delete session JSON
        try:
            _s3().delete_object(Bucket=S3_BUCKET, Key=_s3_session_key(session_id))
        except Exception as exc:
            log.error("S3 delete session error: %s", exc)
        # Delete all artifacts for this session
        try:
            paginator = _s3().get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=f"{S3_PREFIX}/artifacts/{session_id}_"):
                keys = [{"Key": o["Key"]} for o in page.get("Contents", [])]
                if keys:
                    _s3().delete_objects(Bucket=S3_BUCKET, Delete={"Objects": keys})
        except Exception as exc:
            log.error("S3 delete artifacts error: %s", exc)
    else:
        # Local filesystem
        p = session_path(session_id)
        if p.exists():
            p.unlink()
        for f in list(ARTIFACTS_DIR.glob(f"{session_id}_*.pptx")) + \
                  list(ARTIFACTS_DIR.glob(f"{session_id}_*.docx")):
            f.unlink(missing_ok=True)

    # Remove from in-memory room code map
    if room_code and room_code in _room_code_map:
        del _room_code_map[room_code]

    log.info("Deleted session %s and its artifacts", session_id)
    return jsonify({"deleted": session_id})


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


# ── Artifact generation ─────────────────────────────────────────────────────────

def _parse_markdown_sections(md: str) -> list[dict]:
    """Split markdown into sections: [{title, bullets}].
    Treats ## headings as section titles and collects body lines as bullets."""
    sections: list[dict] = []
    current: dict | None = None
    for line in md.splitlines():
        line = line.strip()
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {"title": line[3:].strip(), "bullets": []}
        elif line.startswith("# "):
            if current:
                sections.append(current)
            current = {"title": line[2:].strip(), "bullets": []}
        elif current is not None and line:
            # strip leading markdown list markers
            text = line.lstrip("-*• ").strip()
            if text:
                current["bullets"].append(text)
    if current:
        sections.append(current)
    return sections


def _safe_filename(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    import re
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text)[:40]


def _generate_docx(session: dict, ex_id: str, ex_meta: dict, summary_text: str) -> Path:
    """Create a .docx summary and return its path."""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    sections = _parse_markdown_sections(summary_text)
    if sections:
        for sec in sections:
            doc.add_heading(sec["title"], 2)
            for bullet in sec["bullets"]:
                doc.add_paragraph(bullet, style="List Bullet")
    else:
        # fallback: raw text
        for line in summary_text.splitlines():
            if line.strip():
                doc.add_paragraph(line.strip())

    slug = _safe_filename(ex_meta.get("name", ex_id))
    filename = f"{session['session_id']}_{slug}.docx"
    if _s3_enabled():
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        key = f"{S3_PREFIX}/artifacts/{filename}"
        _s3().put_object(
            Bucket=S3_BUCKET, Key=key, Body=buf.read(),
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        log.info("Uploaded DOCX to S3: %s", key)
        return Path(filename)
    out_path = ARTIFACTS_DIR / filename
    doc.save(str(out_path))
    return out_path


def _generate_pptx(session: dict, ex_id: str, ex_meta: dict, summary_text: str) -> Path:
    """Create a .pptx summary and return its path.

    Layout strategy:
    - Process maps (asis/tobe): swimlane rows — one lane per section, sticky notes filling lane.
    - All other exercises: split layout — left 58% text panel, right 42% sticky-note cluster.
    Sticky notes are coloured rectangles with a shadow offset, arranged in a grid.
    """
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    prs = Presentation()
    prs.slide_width  = Inches(13.33)
    prs.slide_height = Inches(7.5)

    LILLY_RED  = RGBColor(0xCC, 0x00, 0x00)
    WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
    DARK       = RGBColor(0x1A, 0x1A, 0x1A)
    LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)

    STICKY_COLORS = [
        RGBColor(0xFF, 0xF0, 0x6A),  # yellow
        RGBColor(0xA8, 0xD8, 0xFF),  # light blue
        RGBColor(0xA8, 0xF0, 0xC0),  # light green
        RGBColor(0xFF, 0xCC, 0xA8),  # peach
        RGBColor(0xFF, 0xA8, 0xC8),  # pink
        RGBColor(0xD4, 0xA8, 0xFF),  # lavender
    ]

    blank = prs.slide_layouts[6]  # blank layout

    SWIMLANE_EXERCISES   = {"asis_process_map", "tobe_process_map"}
    EMPATHY_MAP_EXERCISES = {"empathy_maps"}
    TEXT_ONLY_EXERCISES  = {"intros_outcomes"}

    # Quadrant label → sticky color index
    QUADRANT_META = {
        "SAYS":   (0, RGBColor(0xFF, 0xF0, 0x6A)),   # yellow
        "DOES":   (1, RGBColor(0xA8, 0xD8, 0xFF)),   # blue
        "THINKS": (2, RGBColor(0xA8, 0xF0, 0xC0)),   # green
        "FEELS":  (3, RGBColor(0xFF, 0xCC, 0xA8)),   # peach
    }

    def _add_header(slide, title_text: str):
        header = slide.shapes.add_shape(
            1, Inches(0), Inches(0), Inches(13.33), Inches(1.1)
        )
        header.fill.solid()
        header.fill.fore_color.rgb = LILLY_RED
        header.line.fill.background()
        tf = header.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top  = Inches(0.15)
        p = tf.paragraphs[0]
        p.text = title_text
        p.alignment = PP_ALIGN.LEFT
        r = p.runs[0]
        r.font.size = Pt(24)
        r.font.bold = True
        r.font.color.rgb = WHITE

    def _add_sticky(slide, text: str, left, top, width, height, color: RGBColor):
        """Draw a sticky-note rectangle with shadow and scaled text to prevent overflow."""
        # Shadow rectangle
        shadow_offset = Inches(0.07)
        sh = slide.shapes.add_shape(
            1,
            left + shadow_offset, top + shadow_offset, width, height
        )
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
        sh.line.fill.background()

        # Scale font down for longer text; hard-truncate as last resort
        char_count = len(text)
        if char_count <= 60:
            font_pt = 10
        elif char_count <= 100:
            font_pt = 9
        else:
            font_pt = 8
            if char_count > 140:
                text = text[:137] + "…"

        # Main sticky rectangle
        rect = slide.shapes.add_shape(1, left, top, width, height)
        rect.fill.solid()
        rect.fill.fore_color.rgb = color
        rect.line.fill.background()

        tf = rect.text_frame
        tf.word_wrap = True
        tf.margin_left  = Inches(0.08)
        tf.margin_right = Inches(0.08)
        tf.margin_top   = Inches(0.06)
        p = tf.paragraphs[0]
        p.text = text
        p.alignment = PP_ALIGN.LEFT
        r = p.runs[0]
        r.font.size  = Pt(font_pt)
        r.font.color.rgb = DARK

    def _add_text_panel(slide, bullets: list[str], full_width: bool = False):
        """Bullet text panel. full_width=True spans the whole slide (no sticky cluster)."""
        panel_w = Inches(12.6) if full_width else Inches(7.2)
        panel = slide.shapes.add_textbox(
            Inches(0.35), Inches(1.25), panel_w, Inches(5.9)
        )
        panel.text_frame.word_wrap = True
        first = True
        for bullet in bullets[:14]:
            if first:
                p = panel.text_frame.paragraphs[0]
                first = False
            else:
                p = panel.text_frame.add_paragraph()
            p.text = f"• {bullet}"
            p.space_after = Pt(5)
            r = p.runs[0]
            r.font.size = Pt(14)
            r.font.color.rgb = DARK

    def _add_sticky_cluster(slide, bullets: list[str]):
        """Right-side sticky-note cluster (3-column grid)."""
        RIGHT_LEFT   = Inches(7.85)
        TOP_Y        = Inches(1.3)
        COLS         = 3
        STICKY_W     = Inches(1.55)
        STICKY_H     = Inches(1.35)
        COL_GAP      = Inches(0.12)
        ROW_GAP      = Inches(0.18)
        MAX_STICKIES = 12

        for i, bullet in enumerate(bullets[:MAX_STICKIES]):
            col = i % COLS
            row = i // COLS
            left = RIGHT_LEFT + col * (STICKY_W + COL_GAP)
            top  = TOP_Y + row * (STICKY_H + ROW_GAP)
            color = STICKY_COLORS[i % len(STICKY_COLORS)]
            _add_sticky(slide, bullet, left, top, STICKY_W, STICKY_H, color)

    def _add_swimlane_slide(section_list: list[dict]):
        """One slide with horizontal swimlanes, one lane per section."""
        slide = prs.slides.add_slide(blank)
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = LIGHT_GRAY

        _add_header(slide, ex_meta.get("name", ex_id))

        LANE_LEFT    = Inches(0)
        LABEL_W      = Inches(1.5)
        CONTENT_LEFT = Inches(1.55)
        CONTENT_W    = Inches(11.7)
        TOP_Y        = Inches(1.15)
        AVAILABLE_H  = Inches(6.2)

        n_lanes = max(len(section_list), 1)
        lane_h  = AVAILABLE_H / n_lanes
        STICKY_W = Inches(1.5)
        STICKY_H = min(lane_h - Inches(0.2), Inches(1.3))
        MAX_PER_LANE = 7

        for lane_i, sec in enumerate(section_list):
            lane_top = TOP_Y + lane_i * lane_h

            # Lane background (alternating)
            lane_bg_color = RGBColor(0xF0, 0xF0, 0xF0) if lane_i % 2 == 0 else RGBColor(0xE4, 0xE4, 0xE4)
            bg_rect = slide.shapes.add_shape(1, LANE_LEFT, lane_top, Inches(13.33), lane_h)
            bg_rect.fill.solid(); bg_rect.fill.fore_color.rgb = lane_bg_color
            bg_rect.line.fill.background()

            # Lane label
            label_box = slide.shapes.add_textbox(Inches(0.05), lane_top + Inches(0.05), LABEL_W, lane_h - Inches(0.1))
            label_box.text_frame.word_wrap = True
            p = label_box.text_frame.paragraphs[0]
            p.text = sec["title"]
            r = p.runs[0]; r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = DARK

            # Sticky notes in lane
            bullets = sec["bullets"][:MAX_PER_LANE]
            COL_GAP = Inches(0.1)
            for b_i, bullet in enumerate(bullets):
                left  = CONTENT_LEFT + b_i * (STICKY_W + COL_GAP)
                top   = lane_top + (lane_h - STICKY_H) / 2
                color = STICKY_COLORS[b_i % len(STICKY_COLORS)]
                _add_sticky(slide, bullet, left, top, STICKY_W, STICKY_H, color)

    def _add_empathy_map_slide(persona_section: dict):
        """2×2 quadrant slide for one persona (Says/Does/Thinks/Feels)."""
        slide = prs.slides.add_slide(blank)
        bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = LIGHT_GRAY
        _add_header(slide, f"{ex_meta.get('name', ex_id)}: {persona_section['title']}")

        # Layout: 2 columns × 2 rows filling the content area
        TOP_Y    = Inches(1.2)
        AVAIL_W  = Inches(13.1)
        AVAIL_H  = Inches(6.1)
        COL_W    = AVAIL_W / 2
        ROW_H    = AVAIL_H / 2
        GAP      = Inches(0.12)
        STICKY_W = Inches(1.55)
        STICKY_H = Inches(0.9)

        QUADRANT_ORDER = ["SAYS", "DOES", "THINKS", "FEELS"]
        QUADRANT_COLORS = {
            "SAYS":   RGBColor(0xFF, 0xF0, 0x6A),
            "DOES":   RGBColor(0xA8, 0xD8, 0xFF),
            "THINKS": RGBColor(0xA8, 0xF0, 0xC0),
            "FEELS":  RGBColor(0xFF, 0xCC, 0xA8),
        }
        QUADRANT_POS = {
            "SAYS":   (Inches(0.1),         TOP_Y),
            "DOES":   (Inches(0.1) + COL_W, TOP_Y),
            "THINKS": (Inches(0.1),         TOP_Y + ROW_H),
            "FEELS":  (Inches(0.1) + COL_W, TOP_Y + ROW_H),
        }

        # Group bullets by quadrant keyword prefix (SAYS:/DOES:/THINKS:/FEELS:)
        quadrant_bullets: dict[str, list[str]] = {q: [] for q in QUADRANT_ORDER}
        for bullet in persona_section["bullets"]:
            for q in QUADRANT_ORDER:
                prefix = f"**{q}:**"
                if bullet.upper().startswith(q + ":") or bullet.startswith(prefix):
                    clean = bullet.split(":", 1)[-1].strip().lstrip("*").strip()
                    quadrant_bullets[q].append(clean)
                    break
            else:
                # Unclassified — append to SAYS as fallback
                quadrant_bullets["SAYS"].append(bullet)

        for q in QUADRANT_ORDER:
            qx, qy = QUADRANT_POS[q]
            color = QUADRANT_COLORS[q]

            # Quadrant label background strip
            label_rect = slide.shapes.add_shape(1, qx, qy, COL_W - GAP, Inches(0.35))
            label_rect.fill.solid(); label_rect.fill.fore_color.rgb = color
            label_rect.line.fill.background()
            tf = label_rect.text_frame
            p = tf.paragraphs[0]; p.text = q
            r = p.runs[0]; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = DARK

            # Sticky notes for this quadrant
            bullets = quadrant_bullets[q][:6]
            COLS = 3
            INNER_TOP = qy + Inches(0.4)
            for i, b in enumerate(bullets):
                col = i % COLS
                row = i // COLS
                bx = qx + col * (STICKY_W + Inches(0.08))
                by = INNER_TOP + row * (STICKY_H + Inches(0.1))
                _add_sticky(slide, b, bx, by, STICKY_W, STICKY_H, color)

    # ── Build slides ─────────────────────────────────────────────────────────────
    sections = _parse_markdown_sections(summary_text)
    if not sections:
        sections = [{"title": "Summary", "bullets": [l.strip() for l in summary_text.splitlines() if l.strip()]}]

    if ex_id in SWIMLANE_EXERCISES:
        # All sections → single swimlane slide (or multiple if many sections)
        LANES_PER_SLIDE = 5
        for chunk_start in range(0, len(sections), LANES_PER_SLIDE):
            _add_swimlane_slide(sections[chunk_start:chunk_start + LANES_PER_SLIDE])
    elif ex_id in EMPATHY_MAP_EXERCISES:
        # One 2×2 quadrant slide per persona; last section (Common Threads) uses split layout
        for sec in sections:
            if sec["title"].lower().startswith("common thread"):
                slide = prs.slides.add_slide(blank)
                bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = LIGHT_GRAY
                _add_header(slide, sec["title"])
                _add_text_panel(slide, sec["bullets"])
                _add_sticky_cluster(slide, sec["bullets"])
            else:
                _add_empathy_map_slide(sec)
    elif ex_id in TEXT_ONLY_EXERCISES:
        # Text-only: full-width bullet panel, no sticky cluster
        for sec in sections:
            slide = prs.slides.add_slide(blank)
            bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = LIGHT_GRAY
            _add_header(slide, sec["title"])
            _add_text_panel(slide, sec["bullets"], full_width=True)
    else:
        # Split layout: one slide per section
        for sec in sections:
            slide = prs.slides.add_slide(blank)
            bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = LIGHT_GRAY

            _add_header(slide, sec["title"])
            _add_text_panel(slide, sec["bullets"])
            _add_sticky_cluster(slide, sec["bullets"])

    slug = _safe_filename(ex_meta.get("name", ex_id))
    filename = f"{session['session_id']}_{slug}.pptx"
    if _s3_enabled():
        buf = io.BytesIO()
        prs.save(buf)
        buf.seek(0)
        key = f"{S3_PREFIX}/artifacts/{filename}"
        _s3().put_object(
            Bucket=S3_BUCKET, Key=key, Body=buf.read(),
            ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        log.info("Uploaded PPTX to S3: %s", key)
        return Path(filename)
    out_path = ARTIFACTS_DIR / filename
    prs.save(str(out_path))
    return out_path


def _generate_artifacts(session: dict, ex_id: str, ex_meta: dict, summary_text: str) -> list[str]:
    """Generate PPTX + DOCX for a summary. Returns list of filenames created."""
    created = []
    try:
        p = _generate_pptx(session, ex_id, ex_meta, summary_text)
        created.append(p.name)
        log.info("Generated PPTX: %s", p.name)
    except Exception as e:
        log.error("PPTX generation failed: %s", e)
    try:
        d = _generate_docx(session, ex_id, ex_meta, summary_text)
        created.append(d.name)
        log.info("Generated DOCX: %s", d.name)
    except Exception as e:
        log.error("DOCX generation failed: %s", e)
    return created


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

    # Generate PPTX + DOCX artifacts in background
    ex_meta_full = get_exercise_meta(ex_id) or {}
    _generate_artifacts(s, ex_id, ex_meta_full, summary_text)

    socketio.emit("summary_ready", {
        "exercise_id": ex_id,
        "summary_text": summary_text,
    }, room=session_id)

    log.info("Summary generated for session %s exercise %s", session_id, ex_id)
    return jsonify({"exercise_id": ex_id, "summary_text": summary_text})


@app.route("/api/sessions/<session_id>/artifacts")
def list_artifacts(session_id):
    """List all PPTX/DOCX artifacts for a session."""
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    result = []
    prefix_str = session_id  # used for slug parsing

    if _s3_enabled():
        s3_prefix = f"{S3_PREFIX}/artifacts/{session_id}_"
        try:
            paginator = _s3().get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=s3_prefix):
                for obj in page.get("Contents", []):
                    fname = obj["Key"].split("/")[-1]
                    ext   = fname.rsplit(".", 1)[-1].upper()
                    stem  = fname.rsplit(".", 1)[0]
                    slug  = stem[len(prefix_str) + 1:]
                    label = slug.replace("_", " ").title()
                    result.append({
                        "filename": fname,
                        "label":    label,
                        "type":     ext,
                        "size":     obj["Size"],
                        "url":      f"/api/sessions/{session_id}/artifacts/{fname}",
                    })
        except Exception as exc:
            log.error("list_artifacts S3 error: %s", exc)
    else:
        files = sorted(ARTIFACTS_DIR.glob(f"{session_id}_*.pptx")) + \
                sorted(ARTIFACTS_DIR.glob(f"{session_id}_*.docx"))
        for f in files:
            ext   = f.suffix.upper().lstrip(".")
            slug  = f.stem[len(prefix_str) + 1:]
            label = slug.replace("_", " ").title()
            result.append({
                "filename": f.name,
                "label":    label,
                "type":     ext,
                "size":     f.stat().st_size,
                "url":      f"/api/sessions/{session_id}/artifacts/{f.name}",
            })

    # Sort: PPTX before DOCX, then alphabetically by label
    result.sort(key=lambda a: (a["label"], a["type"]))
    return jsonify(result)


@app.route("/api/sessions/<session_id>/artifacts/<filename>")
def download_artifact(session_id, filename):
    """Download a specific artifact — proxies from S3 or serves from disk."""
    if not filename.startswith(session_id) or ".." in filename:
        return jsonify({"error": "Not found"}), 404
    if _s3_enabled():
        key = f"{S3_PREFIX}/artifacts/{filename}"
        try:
            obj  = _s3().get_object(Bucket=S3_BUCKET, Key=key)
            data = obj["Body"].read()
            ext  = filename.rsplit(".", 1)[-1].lower()
            ct   = {
                "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }.get(ext, "application/octet-stream")
            return Response(
                data,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "Content-Type": ct,
                },
            )
        except Exception as exc:
            log.error("S3 download error: %s", exc)
            return jsonify({"error": "File not found"}), 404
    return send_from_directory(str(ARTIFACTS_DIR), filename, as_attachment=True)


@app.route("/api/sessions/<session_id>/artifacts/<filename>", methods=["DELETE"])
def delete_artifact(session_id, filename):
    """Delete a specific artifact file."""
    if not filename.startswith(session_id) or ".." in filename:
        return jsonify({"error": "Not found"}), 404
    if _s3_enabled():
        key = f"{S3_PREFIX}/artifacts/{filename}"
        try:
            _s3().delete_object(Bucket=S3_BUCKET, Key=key)
            log.info("Deleted S3 artifact: %s", key)
            return jsonify({"deleted": filename})
        except Exception as exc:
            log.error("S3 delete error: %s", exc)
            return jsonify({"error": "Delete failed"}), 500
    path = ARTIFACTS_DIR / filename
    if not path.exists():
        return jsonify({"error": "File not found"}), 404
    path.unlink()
    log.info("Deleted artifact: %s", filename)
    return jsonify({"deleted": filename})


@app.route("/api/sessions/<session_id>/goto", methods=["POST"])
def goto_exercise(session_id):
    """Jump the session to any exercise by index."""
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    body = request.json or {}
    try:
        target = int(body["index"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "index required"}), 400

    max_idx = len(s["exercise_order"]) - 1
    if not (0 <= target <= max_idx):
        return jsonify({"error": f"index must be 0–{max_idx}"}), 400

    old_idx = s["current_exercise_index"]
    if old_idx != target:
        s["exercises"][s["exercise_order"][old_idx]]["status"] = "completed" if target > old_idx else "pending"
        s["current_exercise_index"] = target
        s["exercises"][s["exercise_order"][target]]["status"] = "active"
        save_session(s)

    new_ex_id = s["exercise_order"][target]
    ex_meta = get_exercise_meta(new_ex_id) or {}
    socketio.emit("exercise_changed", {
        "exercise_id": new_ex_id,
        "index": target,
        "exercise_meta": ex_meta,
    }, room=session_id)

    log.info("Session %s jumped to exercise %d (%s)", session_id, target, new_ex_id)
    return jsonify({"current_exercise_index": target, "exercise_id": new_ex_id})


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
    safe_name = s["session_name"].encode("ascii", "ignore").decode().replace(" ", "_")[:40].strip("_") or session_id[:8]
    filename  = f"DTW_{safe_name}_{session_id[:8]}.json"
    resp = app.response_class(
        response=json.dumps(s, indent=2, ensure_ascii=False),
        status=200,
        mimetype="application/json",
    )
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@app.route("/api/sessions/<session_id>/export-chat", methods=["GET"])
def export_chat_log(session_id):
    """Export all chat messages grouped by exercise as a .docx file."""
    s = load_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    all_ex_meta = load_exercises()

    # python-docx uses lxml which segfaults under eventlet's monkey-patch.
    # subprocess.run() also deadlocks inside eventlet green threads.
    # Fix: run the blocking subprocess call in a real OS thread via tpool.execute()
    # so eventlet's patched I/O primitives are never involved.
    # All subprocess I/O uses temp files (no pipes at all).
    helper = BASE_DIR / "build_chat_docx.py"
    s_json   = json.dumps(s, ensure_ascii=False)
    ex_json  = json.dumps(all_ex_meta)

    def _build_docx():
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as sess_f:
            sess_f.write(s_json)
            sess_path = sess_f.name
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as out_f:
            out_path = out_f.name
        with tempfile.NamedTemporaryFile(suffix=".err", delete=False) as err_f:
            err_path = err_f.name
        try:
            with open(out_path, "wb") as out_fh, open(err_path, "wb") as err_fh:
                proc = subprocess.run(
                    [sys.executable, str(helper), sess_path, ex_json],
                    stdout=out_fh,
                    stderr=err_fh,
                    timeout=30,
                )
            err_text = open(err_path).read() if proc.returncode != 0 else ""
            return proc.returncode, err_text, open(out_path, "rb").read()
        finally:
            for p in (sess_path, out_path, err_path):
                try:
                    os.unlink(p)
                except OSError:
                    pass

    returncode, err_text, docx_bytes = eventlet.tpool.execute(_build_docx)
    if returncode != 0:
        log.error("build_chat_docx failed: %s", err_text)
        return jsonify({"error": "Failed to generate document"}), 500

    safe_name = s["session_name"].encode("ascii", "ignore").decode().replace(" ", "_")[:40].strip("_") or session_id[:8]
    filename  = f"DTW_{safe_name}_{session_id[:8]}_ChatLog.docx"

    return Response(
        docx_bytes,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        },
    )


# ── SocketIO Events ────────────────────────────────────────────────────────────

@socketio.on("join_session")
def handle_join(data):
    session_id   = data.get("session_id", "").strip()
    display_name = (data.get("display_name") or "").strip()
    role         = (data.get("role") or "").strip()

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
        s["participants"].append({"name": display_name, "role": role, "joined_at": utcnow()})
        save_session(s)
        socketio.emit("participant_joined", {"name": display_name, "role": role}, room=session_id)
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
    if _s3_enabled():
        log.info("S3 storage enabled: s3://%s/%s/ ✓", S3_BUCKET, S3_PREFIX)
    else:
        log.info("S3 not configured — using local filesystem (set S3_BUCKET in .env to enable)")
        log.info("Sessions directory: %s", SESSIONS_DIR)
    token = _read_keychain_token()
    if token:
        log.info("LLM Gateway configured: %s (model: %s) ✓", LLM_GATEWAY_URL, LLM_MODEL)
    else:
        log.warning("lilly-code keychain token not found — AI summaries disabled until you sign in via VS Code")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False)
