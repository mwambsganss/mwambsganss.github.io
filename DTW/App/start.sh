#!/bin/bash
# DTW App — clean start script
# Usage: ./start.sh
# Kills any stale server processes then starts a fresh instance.

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$APP_DIR/server.log"

echo "Stopping any existing DTW server processes..."
kill -9 $(lsof -ti :5001) 2>/dev/null
sleep 1

REMAINING=$(lsof -ti :5001 2>/dev/null)
if [ -n "$REMAINING" ]; then
  echo "ERROR: Port 5001 still in use by PID(s): $REMAINING"
  exit 1
fi

echo "Starting DTW server..."
cd "$APP_DIR"
python3 server.py >> "$LOG" 2>&1 &
SERVER_PID=$!

sleep 4

if lsof -i :5001 -n -P 2>/dev/null | grep -q LISTEN; then
  echo "✓ DTW server running (PID $SERVER_PID) at http://localhost:5001"
  echo "  Logs: $LOG"
else
  echo "ERROR: Server failed to start. Check $LOG"
  exit 1
fi
