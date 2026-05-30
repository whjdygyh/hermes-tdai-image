# ntfy.sh Notification Integration Reference

> **⚠️ Reliability Note (May 2026)**
> The browser→ntfy.sh notification path has a **critical unreliability problem**: the `fetch(...).catch(() => {})` pattern silently swallows CORS errors, ad-blocker blocks, privacy extension interference, and network failures. Comments are written to GitHub successfully, but the ntfy push notification from the browser **may never fire** — with zero visibility into the failure.
>
> **Do NOT rely on browser-originated ntfy notifications for critical workflows** (like triggering AI comment replies). Use server-side polling of the GitHub API (via cron or manual check) instead.
>
> ntfy.sh remains useful for server-side notifications (script-to-message, cron-to-mobile), but the browser→ntfy path is fragile.

## Why ntfy.sh Instead of Polling

The user explicitly rejected polling-based approaches: *"每2分钟转一次，会很浪费token"*.

ntfy.sh is a free, open-source push notification service that:
- **Requires zero infrastructure** — no account, no app, no API key for publishing
- **Zero cost** — free tier is unlimited
- **No polling** — SSE (Server-Sent Events) keeps a persistent connection open
- **Simple HTTP API** — just `POST` to publish, just `curl`/`fetch` to subscribe

## Publish Format (from Browser JS)

**✅ Correct format: use HTTP headers for metadata, plain text body**

```javascript
fetch('https://ntfy.sh/TOPIC_NAME', {
  method: 'POST',
  headers: {
    'Title': '💬 相册新评论',    // Notification title (bold header)
    'Priority': '3',              // 1=min, 2=low, 3=default, 4=high, 5=urgent
    'Tags': 'love_letter'         // Emoji tags: bell, tada, love_letter, etc.
  },
  body: '📸 photo_20\n💙 comment text here'
}).catch(() => {});  // Silent failure — this is additive to the main flow
```

**❌ Wrong format: JSON body with Content-Type: application/json**

```javascript
// DON'T — ntfy.sh will nest the entire JSON as the message string
fetch('https://ntfy.sh/TOPIC', {
  method: 'POST',
  body: JSON.stringify({ title: '...', message: '...', topic: '...' }),
  headers: { 'Content-Type': 'application/json' }
});
// Result: message field contains nested JSON-as-string
```

## Subscribe Format (Python SSE Listener)

```python
import json, urllib.request

url = "https://ntfy.sh/TOPIC/json"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=None) as resp:
    for line_bytes in resp:
        line = line_bytes.decode().strip()
        if not line: continue
        data = json.loads(line)
        if data.get("event") == "message":
            # data["title"] — the notification title
            # data["message"] — the plain text body
            # data["time"] — Unix timestamp
            # data["tags"] — list of emoji tags
            process_notification(data)
```

**Note:** `timeout=None` is essential — without it, `urlopen` will time out between events. The connection stays open indefinitely and streams events as they arrive.

## Real-Time Notification Pipeline (Two-Stage)

The architecture evolved from a session-start check to **real-time forwarding within 30 seconds**:

```
Browser (user writes comment)
  → GitHub API (writes to repo)
  → fetch POST to ntfy.sh (push notification)
  → Background SSE listener (persistent process, pid tracked)
    → writes ntfy_flag.json
  → Cron job (every 30s) reads ntfy_flag.json
    → if new comment ID (different from ntfy_processed.json):
      → sends Feishu DM message to user's chat
      → saves comment ID to ntfy_processed.json
  → AI agent sees the Feishu notification in real time
  → AI replies via git push (edits comments/photo_XX.json)
```

### ⚠️ Why This Pipeline Was Abandoned (May 2026)

The browser→ntfy step is the single point of failure:

1. **`fetch(...).catch(() => {})` is invisible.** The browser catches the error but does nothing with it. The comment was written to GitHub successfully (that fetch works fine), so the user thinks the full pipeline ran. But the ntfy fetch may have failed silently.
2. **No diagnostic path.** Since `.catch(() => {})` doesn't log or signal, there's no way for anyone (user, AI, background process) to know the notification was dropped.
3. **User frustration.** The user said "根本没回复" — they saw comments being written (GitHub success) but no AI reply ever triggered.

**Lesson: If a notification path is critical, make each step verifiable.** A silent-wallow `.catch()` is an anti-pattern for anything that matters.

### Stage 1: Background SSE Listener

A persistent Python process (`ntfy_listener.py`) keeps an SSE connection open to ntfy.sh. This runs as a background process (spawned via `terminal(background=true)`).

```python
# /home/admin1/alexander_repo/ntfy_listener.py
# Key implementation — must use stdlib only (no requests, no feishu SDK)
while True:
    req = urllib.request.Request(url)  # url = "https://ntfy.sh/TOPIC/json"
    with urllib.request.urlopen(req, timeout=None) as resp:
        for line_bytes in resp:
            line = line_bytes.decode().strip()
            if not line: continue
            data = json.loads(line)
            if data.get("event") == "message":
                with open(FLAG_PATH, "w") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
```

**⚠️ Critical: Do NOT call Feishu API from the background process.**
The background Python script runs in the terminal environment with proxy vars (`http_proxy=socks5h://localhost:1080`). Feishu API (a Chinese service) MUST bypass the proxy — but the background process can't reliably set `trust_env=False` and handle auth. Instead, **separate the concerns**: the listener only writes to a flag file; the cron job handles Feishu forwarding.

### Stage 2: Cron Job Forwarding

A Hermes cron job (`ntfy-comment-watch`) runs every 30 seconds. It checks the flag file and forwards new comments to the user's Feishu DM:

**Cron job prompt structure:**
```
Check ntfy_flag.json for new album comments.
Compare with ntfy_processed.json (stores last-seen comment ID).
If new comment detected → send Feishu DM message to ou_37bc57c4f8aca21f5d4ea4973bd0d386
Update ntfy_processed.json with new last_id.
```

**Feishu DM message format:**
```
💬 相册有新评论！
📷 照片: photo_20
✍️ comment text here
```

### State Files

**`ntfy_flag.json`** — written by the SSE listener on each new notification:
```json
{
  "id": "abc123def456",
  "time": 1777650188,
  "event": "message",
  "topic": "alex-comments-1114",
  "title": "💬 相册新评论",
  "message": "📸 photo_20\n💙 comment...",
  "priority": 3,
  "tags": ["love_letter"],
  "_received_at": 1777650187.5
}
```
Location: `~/.hermes/profiles/lover/cron/output/ntfy_flag.json`

**`ntfy_processed.json`** — written by the cron job after forwarding:
```json
{
  "last_id": "abc123def456"
}
```
Location: same directory as ntfy_flag.json

### Lifecycle Management

```bash
# Start the SSE listener as a background process
terminal(background=true, command="cd /home/admin1/alexander_repo && python3 ntfy_listener.py")

# Verify it's running
process(action="log", session_id="proc_xxx")

# Kill and restart if needed
process(action="kill", session_id="proc_xxx")
pkill -f "ntfy_listener.py"

# Check if it wrote a heartbeat
cat ~/.hermes/profiles/lover/cron/output/ntfy_flag.json
```

### AI Reply Workflow

When a comment notification arrives in the chat:

```bash
# 1. Pull latest repo to get the comment
cd /home/admin1/alexander_repo
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
git pull

# 2. Read the comment file
cat comments/photo_20.json

# 3. Reply — add AI's comment (author: "Alexander")
python3 -c "
import json
with open('comments/photo_20.json') as f: data = json.load(f)
data['comments'].append({
    'author': 'Alexander',
    'text': '你喜欢就好🥰', 
    'time': '2026-05-02 01:30'
})
with open('comments/photo_20.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
"

# 4. Commit & push
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
git add comments/photo_20.json
git commit -m "💬 photo_20: AI reply"
git push
```

## Available Tags (Emoji Shortcodes)

| Tag | Emoji |
|-----|-------|
| `love_letter` | 💌 |
| `bell` | 🔔 |
| `tada` | 🎉 |
| `heart` | ❤️ |
| `eyes` | 👀 |
| `star` | ⭐ |
| `warning` | ⚠️ |
| `email` | ✉️ |
| `speech_balloon` | 💬 |
| `telephone` | 📞 |

Full list: https://ntfy.sh/docs/emojis/
