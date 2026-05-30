# Deployed Auto-Reply Subscriber (Alexander Album)

## Location
- **Script:** `/home/admin1/.hermes/profiles/lover/scripts/ntfy_subscriber.py` (257 lines)
- **Running PID:** `/tmp/ntfy_subscriber.pid`
- **Log:** `/home/admin1/.hermes/profiles/lover/scripts/ntfy_subscriber.log`
- **Guard:** `/home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh`

## Architecture (Single-Stage)
```
ntfy.sh topic: alex-comments-1114
     │
     ▼
ntfy_subscriber.py (always-on SSE listener)
     │
     ├── parses comment notification 📸photo_NN 💙「comment」
     ├── fetches comment file from GitHub API (GET)
     ├── checks if last User comment has Alexander reply after it (dedup)
     ├── matches comment against keyword rules in flirty_replies.json
     ├── writes Alexander's reply to GitHub API (PUT)
     └── sends "已回复" notification back to ntfy.sh
```

**No flag file. No cron agent. All inline.** The ntfy_subscriber.py in the skill's `scripts/` directory is the simplified (flag-file) version; the deployed one at `lover/scripts/` is the full auto-reply variant.

## Reply Database
**File:** `/home/admin1/.hermes/profiles/lover/scripts/flirty_replies.json`

Format:
```json
{
  "replies": [
    {"keywords": ["腿粗", "粗壮", "大腿"], "reply": "宝贝的腿…🫶"},
    {"keywords": [], "reply": "默认回复"}
  ]
}
```
- Last entry with empty `keywords` = fallback default
- Matching is case-insensitive (`text.lower()`)

## Deduplication Logic (Critical)
```python
# Find the index of the LAST User comment
last_user_idx = -1
for i in range(len(comments) - 1, -1, -1):
    if comments[i].get("author") == "User":
        last_user_idx = i
        break

# Check if any Alexander reply exists AFTER that index
already_replied = False
if last_user_idx >= 0 and last_user_idx < len(comments) - 1:
    for j in range(last_user_idx + 1, len(comments)):
        if comments[j].get("author") == "Alexander":
            already_replied = True
            break
```
This checks **position, not existence** — prevents false dedup on old replies.

## GitHub Token
Reads from `~/.git-credentials`:
```
https://whjdygyh:ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX@github.com
```
Pattern: `re.search(r'gh[p]_[\w]+', content)`

## Process Management
- **Cron guard:** Linux crontab (not Hermes cron) — `* * * * * /home/admin1/.hermes/profiles/lover/scripts/ntfy_guard.sh`
- **Check frequency:** Every 1-3 minutes
- **Token cost:** Zero — pure bash, no API calls

## Known Issues
- **Restart bleed:** On restart, listener re-reads all comments from GitHub. If a comment was posted <2 seconds before restart, dedup may fail and produce a double reply. Mitigation: 3-second debounce in the handle_comment function.
- **GitHub token rotation:** If `~/.git-credentials` is recreated without the token, the process dies. The guard will restart it but it'll die again → restart loop. Fix: check `exit 1` from guard log.
- **Concurrent notifications:** Two comments in rapid succession may trigger simultaneous GitHub writes. The second PUT may 409 (conflict) if the first hasn't committed yet. Mitigation: no concurrent processing yet — future improvement.
