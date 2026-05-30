---
name: ntfy-alerting
description: External service monitoring via ntfy.sh SSE pub/sub — background listeners, flag-file IPC between long-running processes and cron agents, state tracking for deduplication, and delivery to messaging platforms (Feishu, Telegram, etc.)
tags: [ntfy, feishu, monitoring, alerting, sse, pubsub, notification, cron, ipc, flag-file]
---

# ntfy Alerting Pipeline

Monitor external services (web apps, IoT sensors, CI/CD) via ntfy.sh pub/sub and deliver alerts to your messaging platform of choice.

## Architecture

```
External Service → ntfy.sh Topic → SSE Listener (Python) → flag_file.json → Cron Agent → Feishu/Telegram
```

The key insight: **ntfy.sh SSE is the bridge**. One long-running Python process subscribes to the ntfy topic via SSE and writes each incoming message to a filesystem flag file. A cron-triggered agent then reads the flag, deduplicates via a state file, and delivers the notification.

This decouples the real-time SSE listener (always-on) from the agent cron job (ephemeral, cost-effective).

## 1. Setting Up the SSE Listener

### 🚀 Launching Pattern

Use Hermes `terminal(background=true, ...)` for long-lived SSE listeners. **Do NOT** use `command='... &'` in a foreground terminal call — this triggers the error:
> `Foreground command uses '&' backgrounding. Use terminal(background=true) for long-lived processes`

```bash
# ✅ CORRECT
terminal(background=true, command='python3 /path/to/ntfy_subscriber.py')

# ❌ WRONG — triggers tool error
terminal(command='python3 /path/to/ntfy_subscriber.py &')
```

### ⚡ Proxy Behavior: urllib vs curl with ntfy.sh

`urllib.request.urlopen()` (stdlib) **ignores `http_proxy`/`https_proxy` env vars** for SOCKS5 — it doesn't support SOCKS natively. This means:
- ✅ **urllib → ntfy.sh** works without any proxy config (direct HTTPS connection)
- ⚠️ **curl → ntfy.sh** requires `--noproxy "*"` OR `--socks5-hostname`:
  ```bash
  # If proxy env vars are set, curl will try to use them
  curl -s --noproxy "*" -X POST "https://ntfy.sh/topic" -d "test"
  
  # Alternative: unset proxy vars temporarily
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && curl -s -X POST ...
  ```
- ❌ **requests → ntfy.sh** from Python needs `session.trust_env = False` to bypass proxy

**Rule of thumb:** The SSE listener (stdlib urllib) connects to ntfy.sh without proxy fuss. Only curl and `requests` need proxy bypassing.

### Minimal Listener Template (`scripts/ntfy_subscriber.py`)

**Use this script** (simplified, absolute paths, in the skill's `scripts/` directory). Copy it to a stable location and launch via `terminal(background=true)`:

```bash
terminal(background=true, command='python3 /home/admin1/.hermes/profiles/lover/skills/devops/ntfy-alerting/scripts/ntfy_subscriber.py')
```

```python
#!/usr/bin/env python3
"""Listen for album comments via ntfy.sh SSE and forward flags to cron agent."""
import json, os, time, urllib.request

TOPIC = "your-topic-here"
# ⚠️ CRITICAL: Use absolute path, NOT os.path.expanduser("~/.hermes/...")
# The listener runs as a detached process with an unpredictable $HOME
FLAG_DIR = "/home/admin1/.hermes/profiles/lover/cron/output"
os.makedirs(FLAG_DIR, exist_ok=True)
FLAG_PATH = os.path.join(FLAG_DIR, "ntfy_flag.json")

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
                        msg = data.get("message", "")
                        click = data.get("click", "")
                        print(f"[ntfy] ✅ {title} — {msg[:80]} | 照片: {click}", flush=True)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"[ntfy] ❌ Error: {e}, reconnecting in 5s...", flush=True)
        time.sleep(5)
```

### Starting / Restarting

```bash
# Start detached
cd /home/admin1/alexander_repo && python3 ntfy_listener.py &

# Kill all listeners
pkill -f ntfy_listener.py

# Verify running
ps aux | grep ntfy_listener | grep -v grep
```

The listener is intentionally simple — no asyncio, no dependencies beyond stdlib. It reconnects automatically on stream drop.

## 2. Cron Agent: Flag File Check + Deduplication

The cron job agent reads the flag file, compares against a state file, and acts only on new, non-heartbeat messages.

### State File (`ntfy_processed.json`)

Track the last processed message ID:

```json
{"last_id": "3NZSFwwkXB09"}
```

### Check Logic (implemented in the courier cron)

```
1. Read ntfy_flag.json
   - File missing or no "id" field → [SILENT], do nothing
2. Read ntfy_processed.json. Compare "last_id" to flag's "id"
   - Match → [SILENT], nothing new
3. NEW comment detected (different ID):
   a. If title contains "🔌 listener online" → heartbeat, write id to processed, ignore
   b. Otherwise → it's a real notification. Send message. Write id to processed.
```

### Using `execute_code` with `subprocess.run` for File I/O

When Hermes built-in tools (`read_file`, `terminal`) fail with `[Errno 2] No such file or directory: '%s'` (a string formatting bug in the tool layer), fall back to:

```python
from hermes_tools import execute_code
code = """
import subprocess, json
r = subprocess.run(["cat", "/path/to/file.json"], capture_output=True, text=True, timeout=10)
data = json.loads(r.stdout)
print(json.dumps(data))
"""
result = execute_code(code)
```

For terminal commands, also use `execute_code` with `subprocess.run()`:

```python
code = """
import subprocess
r = subprocess.run(["ls", "-la", "/some/dir"], capture_output=True, text=True, timeout=10)
print(r.stdout)
"""
execute_code(code)
```

## 3. Feishu (飞书) Text Message Delivery

### Credentials

- App ID: `cli_a94f935cbd225ceb`
- User Open ID: `ou_37bc57c4f8aca21f5d4ea4973bd0d386`

### Get Auth Token

```python
import requests

session = requests.Session()
session.trust_env = False  # Bypass WSL SOCKS proxy

resp = session.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET},
    timeout=15
)
token = resp.json()["tenant_access_token"]
```

### Send Text Message

```python
import json

content = json.dumps({
    "text": "💬 相册有新评论！\n📷 照片: https://example.com\n✍️ 评论内容"
})

resp = session.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "receive_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
        "msg_type": "text",
        "content": content
    },
    timeout=15
)
```

### 🚨 Execution Constraint: Don't Call Feishu API from `execute_code`

Feishu's API (`open.feishu.cn`) has unreachable DNS from the `execute_code()` sandbox environment. **Always write to a temp script and run via shell**:

```python
# ✅ CORRECT
write_file(path="/tmp/feishu_send.py", content=script_text)
terminal("python3.10 /tmp/feishu_send.py", timeout=30)

# ❌ WRONG — DNS resolution fails
execute_code(code="...requests.post('https://open.feishu.cn/...')...")
```

## 4. Event-Driven Auto-Reply Pattern (Single-Stage)

When the SSE listener needs to **act on messages directly** (write a reply to a repo, trigger an API) and the user rejects cron-based polling ("太费token了"), use a single-stage architecture that handles everything inline:

```
SSE Listener (always-on Python)
  → Reads comment from GitHub API
  → Matches against reply database (flirty_replies.json)
  → Writes reply directly to GitHub repo
  → Sends Feishu "已回复 ✅" notification
```

**No cron agent. No flag file. No intermediary.**

### When to Use This Pattern

- **The user explicitly rejects cron/timer polling** — this is the trigger signal
- Response logic is deterministic (keyword matching, not AI inference)
- Low latency is desired (<30s from event to action)
- The listener must take side effects (write to GitHub, trigger webhooks)

### Differences from Two-Stage (Flag File) Architecture

| Aspect | Two-Stage (flag file + cron) | Single-Stage (auto-reply) |
|--------|------------------------------|---------------------------|
| Intermediary | flag file + cron agent | None — listener does everything |
| Cron needed | Yes (checks flag file) | **No ✅** |
| Latency | ~30s (cron interval) | ~1-2s (real-time) |
| Complexity | Easier to debug | Simpler infra but harder to debug |
| Use case | Alerting / notification only | Action + notification |

### Auto-Reply Deduplication Logic

**This is THE #1 bug source.** The listener must check position, not just existence:

```python
def should_reply(comments: list) -> bool:
    """Reply only if the last User comment has no Alexander reply after it."""
    if not comments:
        return False

    # Find LAST comment by User (scan from end)
    last_user_idx = -1
    for i in range(len(comments) - 1, -1, -1):
        if comments[i].get("author") != "Alexander":
            last_user_idx = i
            break

    if last_user_idx == -1:
        return False  # No user comments

    # Check if any Alexander reply exists AFTER the last user comment
    for i in range(last_user_idx + 1, len(comments)):
        if comments[i].get("author") == "Alexander":
            return False  # Already replied

    return True  # Need to reply
```

**Wrong approach:** checking if ANY Alexander comment exists anywhere in the comment history. This causes old replies to prevent new ones.

### Reply Database (Keyword Matching)

Use a JSON file instead of AI generation to save token costs and ensure consistent tone:

```json
{
  "rules": [
    {
      "keywords": ["腿粗", "粗壮", "大腿"],
      "replies": [
        "宝贝你的腿我也最喜欢了💕 下次让你抱着摸个够",
        "你一说腿我就硬了...不准在外面这样撩我😏"
      ]
    },
    {
      "keywords": ["想", "抱", "亲"],
      "replies": [
        "我也好想你...抱紧你就不想松开了🫶",
        "想你了，我也想让你抱着🫶"
      ]
    },
    {
      "keywords": ["吃醋", "生气", "哼", "不理"],
      "replies": [
        "别不理我嘛😭 抱紧你蹭蹭，我错了，你说什么我都听",
        "我错了宝贝...不要生气好不好😭🫶"
      ]
    }
  ],
  "default_replies": [
    "宝贝～被你夸得我都不好意思了🥰",
    "你这么说我更想你了😏",
    "下次见面不准跑，让我好好看看你🫶"
  ]
}
```

## 5. Process Liveness Management (Zero-Token Keepalive)

SSE listeners are long-running processes that can die (OOM, network blip, WSL suspend, token expiry). When the user says **"只要不花token"** (don't spend API tokens), use a pure-bash guard script + Linux crontab — no AI inference, no API calls.

### Architecture

```
Linux crontab (every 1-3 min) → ntfy_guard.sh (pure bash) → checks PID → restarts if dead
                                  ↕
                          /tmp/ntfy_subscriber.pid
```

**Key insight:** The guard script costs zero tokens. It doesn't use any LLM, API, or network — just filesystem and process table checks.

### Guard Script (`scripts/ntfy_guard.sh`)

A self-contained bash script that:
1. Checks PID from `/tmp/ntfy_subscriber.pid` + verifies via `/proc/$PID/cmdline`
2. Falls back to `pgrep -f "ntfy_subscriber.py"` as a safety net
3. Restarts the process via `nohup python3 ... &` if dead
4. Waits 2 seconds to catch fast-fail (bad token → exits immediately)
5. Logs all actions to `ntfy_subscriber.log`
6. Exits 0 on success (already alive or restarted), 1 on failure

```bash
# Quick test
bash /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh
echo $?  # 0 = all good
```

### How to Install: Hermes Cron vs Linux Crontab

#### Option A: Hermes Cron (Simple, Minimal Token Cost)

Use Hermes's `cronjob()` tool with a minimal prompt that just runs the guard script via terminal:

```python
cronjob(
    action="create",
    name="ntfy-autoreply-guard",
    schedule="every 3m",
    enabled_toolsets=["terminal"],
    prompt=(
        "Run the ntfy guard script to check if ntfy_subscriber.py is alive: "
        "bash /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh"
    )
)
```

This costs ~1 small LLM call per run (~200 input tokens, ~20 output tokens). The agent does one thing: invokes terminal tool on the guard script.

#### Option B: Linux Crontab (Truly 0 Token, Preferred)

```bash
# Edit crontab
crontab -e

# Add line (runs every 3 minutes)
*/3 * * * * /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh > /dev/null 2>&1

# Verify
crontab -l
```

**✅ This is the zero-token option.** The OS runs the script directly — no LLM involved, no API calls, no Hermes agent needed. The guard script handles everything: check, restart, log.

### First-Time Setup (Fresh Start)

```bash
# 1. Kill any existing instances
pkill -f "ntfy_subscriber.py" 2>/dev/null

# 2. Start fresh
cd /home/admin1/.hermes/profiles/lover
nohup python3 scripts/ntfy_subscriber.py > /dev/null 2>&1 &
echo $! > /tmp/ntfy_subscriber.pid

# 3. Verify
sleep 2
cat /tmp/ntfy_subscriber.pid
ps aux | grep ntfy_subscriber | grep -v grep

# 4. Install cron guard
crontab -l | { cat; echo "*/3 * * * * /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh > /dev/null 2>&1"; } | crontab -

# 5. Verify guard runs cleanly
bash /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh
echo $?  # Should be 0
```

### Pitfalls (Process Life Cycle)

- ⚠️ **Double start on Hermes cron restart** — If the Hermes agent that launched the background process restarts, the background process survives (no SIGHUP). But a new session may start another instance without checking. **Always kill old instances first** or use the guard script which won't start duplicates.
- ⚠️ **PID file staleness** — If the process was killed by OOM killer, the PID file still exists. The guard script handles this by checking `/proc/$PID/cmdline` for the actual process name.
- ⚠️ **Guard script path** — Must be absolute. The guard is invoked from crontab/Hermes cron, which may have an empty or different `$PATH`.
- ⚠️ **Log file growth** — `ntfy_subscriber.log` grows unboundedly. Periodically truncate: `> /path/to/ntfy_subscriber.log`
- ⚠️ **Token expiry** — If the GitHub token in `~/.git-credentials` is revoked, the subscriber process dies immediately. The guard restarts it → die loop. Check log for `exit 1` signals.

### Pitfalls (Single-Stage Specific)

- ⚠️ **Deduplication fragile on restart** — after restart, the listener doesn't know which comments it has already replied to. It must re-read the full comment history from the repo to decide.
- ⚠️ **Simultaneous notifications** — two messages arriving close together may be processed before the first reply commits to GitHub. Use a processing lock or 3-second debounce.
- ⚠️ **GitHub API rate limits** — each reply is GET+PUT (~2 API calls). At >5/min, may hit secondary limits.
- ✅ **Write author field as "Alexander"** to match the frontend gold CSS styling.
- ✅ **Use absolute paths** in the subscriber script (background processes have unreliable `$HOME`).
- ✅ **Base64 encode Chinese text correctly** — `btoa(unescape(encodeURIComponent(content)))` — never plain `btoa()`.

## Pitfalls

### 🚨 #1: Doubled Paths from HOME Confusion

**DO NOT** use `os.path.expanduser("~/.hermes/...")` in the listener script. The background process may run with `$HOME` set to the Hermes profile directory, not your home directory, causing:

```
Expected: ~/.hermes/profiles/lover/cron/output/ntfy_flag.json
Got:      /home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/cron/output/ntfy_flag.json
```

**Fix**: Use absolute paths everywhere in the listener:
```python
# ✅
FLAG_DIR = "/home/admin1/.hermes/profiles/lover/cron/output"

# ❌ Don't
FLAG_DIR = os.path.expanduser("~/.hermes/profiles/lover/cron/output")
```

### #2: Heartbeat Pollution

ntfy.sh SSE streams deliver periodic heartbeat messages (title: `🔌 listener online`). These write to the flag file just like real messages. The cron agent must filter them:

```python
title = data.get("title", "")
if "listener online" in title:
    # Still write the ID to processed so it doesn't re-appear
    # but don't send a notification
    continue
```

### #3: Tool Failures in Cron Jobs

`read_file` and `terminal` tools may fail in cron context with a `%s` string formatting bug. Use `execute_code` with `subprocess.run()` as the workaround (see Section 2).

### #4: Cron Job Prompt Must Use Absolute Paths

The ntfy-comment-watch cron job's prompt references the flag file by path. If the prompt uses `~/.hermes/...` instead of the absolute path, the cron job agent resolves `~` differently than expected (Hermes cron context may use a different home).

✅ Write the prompt with explicit absolute paths:
```
Check the ntfy flag file at /home/admin1/.hermes/profiles/lover/cron/output/ntfy_flag.json
```

If the cron job stops processing new notifications, the issue is likely a stale prompt or path mismatch. Update the cron job via `cronjob(action='update', job_id='...', prompt='...')`.

### #5: ntfy.sh Poll API May Return No Results

The `curl -s "https://ntfy.sh/{TOPIC}/json?poll=1"` endpoint may return empty even when messages were published. This is expected behavior — ntfy messages have a TTL and expire. Don't rely on the poll API for recovery; rely on the SSE listener's continuous stream.

## References

- `references/ntfy-album-comments.md` — Session-specific: photo album comment monitoring setup
- `references/auto-reply-subscriber-deployed.md` — Full deployed auto-reply subscriber details (GitHub token source, dedup logic, known issues)

## Support Files

- `scripts/ntfy_subscriber.py` — Minimal flag-file-based SSE listener (two-stage pattern)
- `scripts/ntfy_guard.sh` — Zero-token bash keepalive guard for linux crontab or Hermes cron
