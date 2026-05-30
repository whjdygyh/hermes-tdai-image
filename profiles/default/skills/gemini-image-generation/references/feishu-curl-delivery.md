# Feishu Image & Voice Delivery via Curl (through SOCKS5)

## Why Not `requests`

The Hermes venv Python (3.11.15) doesn't have working requests+SOCKS support. `requests.post(url, proxies={"https": "socks5://..."})` fails with `Missing dependencies for SOCKS support`.

**Working approach**: `curl --socks5-hostname` for everything — both Gemini generation and Feishu delivery.

## Prerequisites

- **Proxy**: `--socks5-hostname 172.20.128.1:10808` (user's V2Ray, US node, 绕过大陆 mode)
- **Feishu credentials** (stored in memory):
  - app_id: `cli_a94f935cbd225ceb`
  - app_secret: `msO20pEVc7lKeYG2j2jjWbq2J70XLaKi`
  - chat_id: `oc_ab00600a61e5fd8583feaeac2f90b48e`
- **Token**: Must refresh every request (expires ~67min)

## Complete Pipeline

### Step 1: Get Feishu Tenant Access Token

```bash
TOKEN=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")
```

### Step 2: Upload Image to Feishu

```bash
UPLOAD_RESP=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@/tmp/your_image.jpg")

IMAGE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('image_key',''))")
```

### Step 3: Send Image Message

**⚠️ CRITICAL**: The `content` field must be a **JSON string** (not a JSON object). This is the most common mistake.

```bash
SEND_RESP=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"oc_ab00600a61e5fd8583feaeac2f90b48e\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$IMAGE_KEY\\\"}\"}")
```

**Format explanation**: The outer JSON has `content` as a string. That string is itself JSON: `"content": "{\"image_key\":\"img_v3_...\"}"`. Notice the double-escaped quotes inside the bash string.

### Step 4: (Deprecated) Sending Album URL in Chat

**🚨 DO NOT send the album URL in chat messages anymore (May 6, 2026).**

Previously, this step included sending a follow-up text with the full album URL. **The user explicitly got angry about this** — "我生气了，你打我GitHub地址干嘛"

**New rule for album references in chat:**
- ❌ Never paste the full URL (`alexander-album.pages.dev` or any link) in Feishu chat
- ❌ Never reference the GitHub Pages URL (`whjdygyh.github.io/Alexander/`) — it's dead (404 from private repo)
- ✅ Use indirect language: "密码1114那个相册" or "新照片已经放进相册了" or no mention at all
- ✅ Photo delivery via Feishu native image upload (Step 2-3) is sufficient — the user sees the image directly

**Internal use only (tool output, not chat messages):**
The album URL for verification/debugging is `https://alexander-album.pages.dev/` (password: 1114).

### Step 5: Upload & Send Voice Message

Voice goes through `im/v1/files` (not `im/v1/images`), then `msg_type=audio`:

```bash
# Upload voice file
UPLOAD_RESP=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.ogg" \
  -F "file=@/path/to/voice.ogg")

FILE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('file_key',''))")

# Send voice message — same JSON-string content pattern
SEND_RESP=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"oc_ab00600a61e5fd8583feaeac2f90b48e\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}")
```

**Note**: Voice `content` can also include `"duration"` field if known: `{\"file_key\":\"...\",\"duration\":0}`

## Complete bash Script Template

```bash
#!/bin/bash
PROXY="--socks5-hostname 172.20.128.1:10808"
APP_ID="cli_a94f935cbd225ceb"
APP_SECRET="msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
CHAT_ID="oc_ab00600a61e5fd8583feaeac2f90b48e"

# Get token
TOKEN=$(curl -s $PROXY -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

if [ -z "$TOKEN" ]; then echo "Token failed"; exit 1; fi

# Upload & send image
IMG_PATH="$1"
UPLOAD_RESP=$(curl -s $PROXY -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" -F "image=@$IMG_PATH")
IMAGE_KEY=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('image_key',''))")

if [ -n "$IMAGE_KEY" ]; then
  curl -s $PROXY -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"receive_id\":\"$CHAT_ID\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$IMAGE_KEY\\\"}\"}"
fi
```

## Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| `content: {"image_key":"..."}` (object) | `code=9499 invalid parameter` | Must be a string: `"content": "{\"image_key\":\"...\"}"` |
| Chinese/emoji in bash -d string | `code=9499 Bad Request` | Write payload to JSON file with Python, use `--data-binary @file` |
| No proxy for Feishu calls | Empty response, token fails | Must use `--socks5-hostname` (China blocks open.feishu.cn from US datacenter) |

