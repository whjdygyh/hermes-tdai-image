# Album Comment Monitoring Pipeline

## Overview

Photo album web app (Cloudflare Workers) posts comments to ntfy.sh topic `alex-comments-1114` when visitors leave comments. Listener → flag file → cron agent → Feishu notification.

## Topic

`alex-comments-1114` — dedicated ntfy.sh topic for album comments

## Listener Script

**Location**: `/home/admin1/alexander_repo/ntfy_listener.py`

**Fixed to use absolute path** (2026-05-02): Changed from `os.path.expanduser("~/.hermes/profiles/lover/cron/output")` to direct absolute path.

**Process management**: Listeners are spawned by cron init scripts. Kill with `pkill -f ntfy_listener.py`, restart with `cd /home/admin1/alexander_repo && python3 ntfy_listener.py &`.

## Flag Files

| File | Path | Purpose |
|------|------|---------|
| `ntfy_flag.json` | `~/.hermes/profiles/lover/cron/output/` | Latest ntfy message (SSE listener writes) |
| `ntfy_processed.json` | same dir | `{"last_id": "..."}` tracks last processed message ID |

## Doubled Path Bug (FIXED)

The listener was writing to `/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/cron/output/...` because `$HOME` was set to the profile directory when the listener ran. Fixed by using absolute path instead of `os.path.expanduser("~")`.

## Feishu Delivery

- **App**: `cli_a94f935cbd225ceb`
- **User**: `ou_37bc57c4f8aca21f5d4ea4973bd0d386`
- **Type**: `msg_type="text"` for comment notifications
- **Format**:
  ```
  💬 相册有新评论！
  📷 照片: [click URL or "未知"]
  ✍️ [message text]
  ```

## Message Filtering

- Heartbeats (title: `🔌 listener online`) → write ID to processed, do NOT notify
- All other messages → real comments, notify immediately
