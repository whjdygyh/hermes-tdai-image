#!/bin/bash
# ntfy_guard.sh — Process liveness guard for ntfy_subscriber.py
# Zero-token cost: pure bash, no API calls, no AI inference.
# Designed to run from cron (every 1-5 minutes).
#
# Usage:
#   bash /path/to/ntfy_guard.sh
#   echo $? — 0 = already alive, 0 = restarted successfully, nonzero = error
#
# Works with both the simplified (flag-file) and full (auto-reply) subscriber variants.

SCRIPT_DIR="/home/admin1/.hermes/profiles/lover/scripts"
SCRIPT="$SCRIPT_DIR/ntfy_subscriber.py"
LOG="$SCRIPT_DIR/ntfy_subscriber.log"
PIDFILE="/tmp/ntfy_subscriber.pid"

# === Check 1: PID file + /proc ===
if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        # Verify it's actually the right process (not a recycled PID)
        if grep -q "ntfy_subscriber" /proc/$OLD_PID/cmdline 2>/dev/null; then
            exit 0  # All good
        fi
    fi
    # Stale PID file (process died or recycled)
    rm -f "$PIDFILE"
fi

# === Check 2: pgrep fallback ===
RUNNING_PID=$(pgrep -f "ntfy_subscriber.py" 2>/dev/null | head -1)
if [ -n "$RUNNING_PID" ]; then
    echo "$RUNNING_PID" > "$PIDFILE"
    exit 0  # Found by pgrep
fi

# === Dead — restart ===
echo "[🛡️] $(date '+%Y-%m-%d %H:%M:%S') — ntfy_subscriber not running, restarting..." >> "$LOG"

# Restart from stable directory (absolute path insulates from $HOME quirks)
cd /home/admin1/.hermes/profiles/lover
nohup python3 "$SCRIPT" > /dev/null 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PIDFILE"

echo "[🛡️] $(date '+%Y-%m-%d %H:%M:%S') — Restarted with PID $NEW_PID" >> "$LOG"

# Give it 2 seconds to fail-fast (misconfigured token, etc.)
sleep 2
if ! kill -0 "$NEW_PID" 2>/dev/null; then
    echo "[🛡️] ❌ Restart FAILED — check log at $LOG" >> "$LOG"
    rm -f "$PIDFILE"
    exit 1
fi

echo "[🛡️] ✅ Restart successful: PID $NEW_PID" >> "$LOG"
