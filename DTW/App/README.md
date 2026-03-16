# Design Thinking Workshop App

A real-time, AI-powered collaborative workshop app for facilitators and participants.
Built on Flask + Socket.IO with Claude AI-generated exercise summaries.

## Features

- **17 design thinking exercises** across 5 phases (Understanding → Empathizing → Ideation → Planning → Review)
- **Facilitator controls** — select exercises, set order, advance/go back, trigger AI summaries
- **Real-time chat** per exercise — Teams-style (initials avatar, sender name, timestamp)
- **AI summaries** — Claude generates a structured summary at the end of each exercise, shared with all participants
- **Session persistence** — all messages and summaries saved to JSON files
- **Session export** — download full session data as JSON

## Setup

```bash
cd "DTW/App"
pip3 install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python3 server.py
```

Open **http://localhost:5001** in your browser.

## Usage

### Facilitator

1. Click **Facilitator Login** → **Create New Session**
2. Enter a session name and a passcode (only you will use this)
3. Select which exercises to run and drag to reorder
4. Click **Create Session** — note the **6-character Room Code**
5. Share the room code with participants
6. Use **Next →** and **← Back** to control which exercise is active
7. Click **✦ Generate AI Summary** at the end of each exercise
8. Review the summary and click **Next Exercise →** to continue

### Participant

1. Click **Join a Session**
2. Enter the 6-character room code and your display name
3. Read the exercise instructions in the panel at the top
4. Type your response in the chat and press **Enter** or **Send**
5. When the facilitator generates a summary, it appears automatically

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | — | Required for AI summaries |
| `PORT` | `5001` | Flask server port |
| `FLASK_SECRET_KEY` | auto | Flask session signing key |

## File Structure

```
DTW/App/
├── server.py        — Flask + Socket.IO backend, AI summary generation
├── index.html       — Single-page app (all views)
├── style.css        — Lilly brand design system, Teams-style chat
├── app.js           — Frontend state machine + Socket.IO client
├── exercises.json   — All 17 exercises with metadata and AI prompt hints
├── sessions/        — Auto-created; one JSON file per workshop session
├── requirements.txt
└── .env.example
```

## Exercises

| # | Exercise | Phase |
|---|----------|-------|
| 1 | Hopes & Fears Board | Understanding |
| 2 | Persona Cards | Understanding |
| 3 | Stakeholder Map | Understanding |
| 4 | Empathy Maps | Empathizing & Mapping |
| 5 | As-Is Process Map | Empathizing & Mapping |
| 6 | Needs Statements | Empathizing & Mapping |
| 7 | Assumptions & Questions 2×2 Grid | Ideation & Prioritization |
| 8 | Big Idea Vignettes | Ideation & Prioritization |
| 9 | Prioritization Grid | Ideation & Prioritization |
| 10 | To-Be Process Map | Ideation & Prioritization |
| 11 | Experience-Based Roadmap | Planning & Execution |
| 12 | Hills / Objectives | Planning & Execution |
| 13 | Gantt Roadmap | Planning & Execution |
| 14 | Resource Plan | Planning & Execution |
| 15 | Feedback Grid | Review & Presentation |
| 16 | Executive Summary | Review & Presentation |
| 17 | Workshop Playback Deck | Review & Presentation |

## Session Data Format

Each session is saved to `sessions/session_<uuid>.json`:

```json
{
  "session_id": "...",
  "session_name": "Q2 Banner Workshop",
  "room_code": "AB12CD",
  "exercise_order": ["hopes_fears", "persona_cards", ...],
  "current_exercise_index": 2,
  "participants": [{"name": "Alice", "joined_at": "..."}],
  "exercises": {
    "hopes_fears": {
      "messages": [{"sender": "Alice", "timestamp": "...", "text": "..."}],
      "summary": "## Key Themes\n...",
      "status": "completed"
    }
  }
}
```

## Notes

- The app runs locally; all participants must be on the same network or VPN
- Session files are stored locally in `sessions/` — back them up after the workshop
- AI summaries require an Anthropic API key; rule-based summaries are not available as a fallback
- The facilitator passcode is stored plaintext in the session JSON — this is a workshop facilitation tool, not a security product
