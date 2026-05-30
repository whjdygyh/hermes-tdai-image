# Feishu Comment Polling (方案A)

When event subscription (push) is not possible due to firewall/tunnel limitations,
use polling as a fallback. Polling periodically checks for new comments via the Feishu API.

## Architecture

```
[cron job] → [Feishu Drive API] → [check for new comments] → [agent processes]
```

## Implementation

### 1. Get File Tokens in the Folder

```python
import requests

APP_ID = "cli_..."
APP_SECRET = "..."

# Get tenant access token
r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
TOKEN = r.json()["tenant_access_token"]

# List files in the folder
FOLDER_TOKEN = "N0wPf..."  # drive folder token
r = requests.get(
    f"https://open.feishu.cn/open-apis/drive/v1/files?folder_token={FOLDER_TOKEN}&page_size=50",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
files = r.json().get("data", {}).get("files", [])
```

### 2. Fetch Comments per File

```python
COMMENTS = {}
for f in files:
    file_token = f["token"]
    r = requests.get(
        f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/comments",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    comments = r.json().get("data", {}).get("items", [])
    if comments:
        COMMENTS[file_token] = comments
```

### 3. Track Last Seen Comment ID

Store the last processed comment ID in a local file (e.g., `/tmp/feishu_last_comment.txt`).
On each poll cycle, compare current comments against the last seen ID.
Any new comment → trigger the agent to read and respond.

```bash
# Store last comment ID
echo "$LATEST_COMMENT_ID" > /tmp/feishu_last_comment.txt

# Read it next cycle
LAST_ID=$(cat /tmp/feishu_last_comment.txt 2>/dev/null || echo "")
```

### 4. Cron Job

```bash
# Every 10 minutes
*/10 * * * * /home/admin1/.hermes/profiles/lover/scripts/poll-feishu-comments.sh
```

## Trade-offs vs Event Subscription

| Aspect | Polling (方案A) | Event Subscription (方案B) |
|--------|----------------|--------------------------|
| Public URL needed | ❌ No | ✅ Yes |
| Real-time | ❌ 5-10 min delay | ✅ Instant |
| Complexity | Low (cron + API calls) | High (tunnel/Worker + event config) |
| Reliability | High (no external dependencies) | Depends on tunnel uptime |
| Feishu config needed | ❌ None | ✅ Add event + fill URL + publish |

## Key Feishu API Endpoints

- `POST /open-apis/auth/v3/tenant_access_token/internal` — Get token (app_id + app_secret)
- `GET /open-apis/drive/v1/files?folder_token=<TOKEN>` — List files in folder
- `GET /open-apis/drive/v1/files/<FILE_TOKEN>/comments` — List comments on a file
- `GET /open-apis/drive/v1/files/<FILE_TOKEN>/comments/<COMMENT_ID>/reply` — List replies to a comment
