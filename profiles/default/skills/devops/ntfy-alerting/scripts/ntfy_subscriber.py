#!/usr/bin/env python3
"""
ntfy.sh SSE subscriber — simplified, with absolute paths.

Use this via: terminal(background=true, command='python3 /path/to/ntfy_subscriber.py')

Do NOT use: terminal(command='python3 script.py &')  — this will fail with
"Foreground command uses '&' backgrounding" error.

The listener uses stdlib urllib only (no external dependencies, no proxy issues
with ntfy.sh since urllib ignores SOCKS5 env vars naturally).

FLAG_DIR uses absolute path to avoid the $HOME-resolution bug where the
background process picks up a different ~ than expected.
"""
import json, os, time, urllib.request

TOPIC = "alex-comments-1114"
FLAG_DIR = "/home/admin1/.hermes/profiles/lover/cron/output"
FLAG_FILE = os.path.join(FLAG_DIR, "ntfy_flag.json")

os.makedirs(FLAG_DIR, exist_ok=True)

# Heartbeat — verify connectivity
try:
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=b"listener online",
        headers={"Title": "🔌 listener online", "Priority": "1"},
        method="POST"
    )
    urllib.request.urlopen(req, timeout=10)
except Exception:
    pass

url = f"https://ntfy.sh/{TOPIC}/json"
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
                        with open(FLAG_FILE, "w") as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        title = data.get("title", "")
                        msg = data.get("message", "")[:80]
                        print(f"[ntfy] ✅ {title} — {msg}", flush=True)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"[ntfy] ⚠️ {e}, reconnecting in 5s...", flush=True)
        time.sleep(5)
