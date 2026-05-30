# Feishu Cloud Drive Album Publishing

## Overview

After generating images via Gemini (or any other source), upload them to a Feishu cloud drive folder. This is the user's **sole album solution** — all other approaches (GitHub Pages, Cloudflare Pages, HTML albums) are abandoned.

## Prerequisites

- Feishu Bot credentials: `app_id` + `app_secret` (from memory or config)
- Folder token: the album folder's `folder_token`

## Step 1: Get Tenant Access Token

```bash
RESP=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_xxx","app_secret":"xxx"}')
TOKEN=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")
```

## Step 2: Upload Image

### Required parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `file_name` | Descriptive name, e.g. `32_island_sex.jpg` | Use sequential numbering for album order |
| `parent_type` | `explorer` | Fixed for cloud drive folders |
| `parent_node` | `{FOLDER_TOKEN}` | The album folder's token |
| `size` | File size in bytes | **Required!** Without it → error 1061002 |
| `file` | The binary file | Use `@` syntax in curl |

### Full command

```bash
FILE=/path/to/generated_image.jpg
SIZE=$(stat -c%s "$FILE")
FOLDER_TOKEN="N0wPfG49ZlJCErdjwUUcYdsUnyP"  # Replace with actual token

curl -s -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/upload_all' \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_name=descriptive_name.jpg" \
  -F "parent_type=explorer" \
  -F "parent_node=$FOLDER_TOKEN" \
  -F "size=$SIZE" \
  -F "file=@$FILE"
```

### ⚠️ Critical: Proxy Interference

The server may have proxy env vars set (`https_proxy`, `http_proxy`). These cause Feishu API calls to fail since Feishu is accessed directly (no proxy needed). **Always clear proxy env vars:**

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY curl ...
```

## Step 3: Grant Folder Permissions (if needed)

To give a user access to the folder:

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/${FOLDER_TOKEN}/members?type=folder" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "member_type": "openid",
    "member_id": "ou_{USER_OPENID}",
    "perm": "full_access"
  }'
```

| Parameter | Value | Notes |
|-----------|-------|-------|
| `member_type` | `openid` | User's Feishu open ID |
| `member_id` | `ou_xxx` | The user's open ID |
| `perm` | `full_access` | Full read/write permissions |

## Album Naming Convention

Use sequential numbering for album organization:
- `01_evening_sofa.jpg`, `02_legs_sofa.jpg`, ..., `29_saturday_cafe_americano.jpg`
- Continue from the highest existing number + 1

## Folder Link (user-facing)

Share the folder link with the user so they can browse directly in Feishu:
```
https://my.feishu.cn/drive/folder/{FOLDER_TOKEN}
```

## Error Reference

| Code | Message | Cause | Fix |
|------|---------|-------|-----|
| 1061002 | params error | **Missing `size`** OR **wrong `parent_type`** | Add `size=$(stat -c%s "$FILE")`. AND ensure `parent_type=explorer` NOT `folder` |
| 99991663 | permission denied | Token expired or lacks permission | Refresh tenant_access_token |
| Any network error | connection timeout | Proxy interference | Clear proxy env vars |

## 🚨 Hard-Earned Pitfalls (May 7, 2026)

### ⚠️ parent_type MUST be explorer, NOT folder

The most common mistake. The `parent_type` parameter value must be `explorer` — not `folder`, not `drive_file`. Using `folder` causes error 1061002 with a vague "params error" message. This is counterintuitive but confirmed from Feishu API spec.

```bash
# ❌ WRONG — causes error 1061002
-F "parent_type=folder"

# ✅ CORRECT
-F "parent_type=explorer"
```

### ⚠️ size must be exact bytes, not rounded

```bash
SIZE=$(stat -c%s "$FILE")   # ✅ correct
-F "size=$SIZE"              # pass as form field, NOT in JSON
```

### ⚠️ Clear proxy env vars before EVERY curl call

The server has proxy env vars that interfere with Feishu. Always prepend:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl ... [rest of command]
```
