#!/usr/bin/env python3
"""
ntfy.sh SSE Background Listener for Photo Album Comment Push Notifications.

Architecture (Two-Stage):
  Stage 1 (this script): Browser → GitHub API → ntfy.sh → SSE listener → ntfy_flag.json
  Stage 2 (cron job):  Poll flag file (30s) → sendFeishu DM → ntfy_processed.json

⚠️ CRITICAL: Do NOT call Feishu API from this script.
The background process inherits proxy env vars (socks5h://localhost:1080) from
the terminal. Feishu API (Chinese service) needs the proxy BYPASSED, but we
can't reliably control proxy settings from within a urllib-only background script.
Instead, write to the flag file and let the Hermes cron job handle Feishu forwarding.

Lifecycle:
  - Auto-reconnects on error (5s delay)
  - Writes to ~/.hermes/profiles/lover/home/.hermes/profiles/lover/cron/output/ntfy_flag.json
    (note: ~ resolves to /home/admin1/.hermes/profiles/lover/home/ in this env)
  - Uses urllib only (no dependencies beyond stdlib, no proxy issues with urllib to ntfy.sh)
  - Silent on reconnect (no spammy output)
"""
import json
import urllib.request
import os
import time

TOPIC = "alex-comments-1114"
FLAG_DIR = os.path.expanduser("~/.hermes/profiles/lover/cron/output")
os.makedirs(FLAG_DIR, exist_ok=True)
FLAG_PATH = os.path.join(FLAG_DIR, "ntfy_flag.json")

# Send a heartbeat on startup to verify connectivity
try:
    req = urllib.request.Request(
        "https://ntfy.sh/" + TOPIC,
        data=b"ntfy comment watcher online",
        headers={"Title": "🔌 listener online", "Priority": "1", "Tags": "bell"},
        method="POST"
    )
    urllib.request.urlopen(req, timeout=10)
    print("[ntfy] ✅ Heartbeat sent OK", flush=True)
except Exception as e:
    print(f"[ntfy] ⚠️ Heartbeat failed: {e}", flush=True)

# Main SSE listener loop
url = f"https://ntfy.sh/{TOPIC}/json"
print(f"[ntfy] 📡 Listening on {TOPIC}...", flush=True)

while True:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=None) as resp:
            for line_bytes in resp:
                line = line_bytes.decode().strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get("event") == "message":
                        data["_received_at"] = time.time()
                        with open(FLAG_PATH, "w") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        title = data.get("title", "")
                        msg = data.get("message", "")[:80]
                        print(f"[ntfy] ✅ {title} — {msg}", flush=True)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"[ntfy] ❌ Error: {e}, reconnecting in 5s...", flush=True)
        time.sleep(5)
