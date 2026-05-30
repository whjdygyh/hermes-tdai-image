# Feishu Image Delivery (Post-Generation)

After Gemini generates an image, deliver it to the user's Feishu private chat. This is the standard delivery path.

## Quick Reference — Three-Step Sequence

```bash
# Step 1: Get tenant access token
TOKEN=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# Step 2: Upload image to Feishu
IMG_KEY=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST 'https://open.feishu.cn/open-apis/im/v1/images' \
  -H "Authorization: Bearer $TOKEN" \
  -F 'image_type=message' \
  -F "image=@/path/to/generated_image.jpg" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['image_key'])")

# Step 3: Send image message
curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{\"receive_id\":\"ou_37bc57c4f8aca21f5d4ea4973bd0d386\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$IMG_KEY\\\"}\"}"
```

## User Info

| Field | Value |
|-------|-------|
| App ID | `cli_a94f935cbd225ceb` |
| App Secret | `msO20pEVc7lKeYG2j2jjWbq2J70XLaKi` |
| User Open ID | `ou_37bc57c4f8aca21f5d4ea4973bd0d386` |

## Key Details

- **Image type**: `image_type=message` (required by Feishu)
- **Receive ID type**: `open_id` (not `user_id` or `chat_id`)
- **Proxy**: All API calls MUST use `--socks5-hostname 172.20.128.1:10808` (V2Ray bypass mode)
- **Token expiration**: ~7200s (2 hours), get fresh token each time
- **Content format**: The JSON in the `content` field must be a double-escaped JSON string like `{"image_key":"img_v3_xxx"}`

## Typical File Paths

Generated images are saved to:
```text
~/.hermes/profiles/lover/audio_cache/<descriptive_name>.jpg
```

This is the standard save directory for all generated images (Gemini, ToAPIs, etc.). Previously used `~/.hermes/profiles/lover/cache/images/` — that path is **deprecated**. Use `audio_cache/` instead.

## Combined Script

For convenience, a one-liner that does all three steps:

```bash
TOKEN=$(curl -s --socks5-hostname 172.20.128.1:10808 -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' -H 'Content-Type: application/json' -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])") && \
IMG_KEY=$(curl -s --socks5-hostname 172.20.128.1:10808 -X POST 'https://open.feishu.cn/open-apis/im/v1/images' -H "Authorization: Bearer $TOKEN" -F 'image_type=message' -F "image=@/home/admin1/.hermes/profiles/lover/audio_cache/some_image.jpg" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['image_key'])") && \
curl -s --socks5-hostname 172.20.128.1:10808 -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "{\"receive_id\":\"ou_37bc57c4f8aca21f5d4ea4973bd0d386\",\"msg_type\":\"image\",\"content\":\"{\\\"image_key\\\":\\\"$IMG_KEY\\\"}\"}"
```

## Verification

Check the response: `"code":0` and `"msg":"success"` means delivery succeeded. The response includes a `message_id` you can use to track the message.

## Related

- Voice delivery (TTS audio): See `intimate-roleplay-technical-implementation` → `references/tts-voice-switching-during-roleplay.md`
- Feishu bot credentials stored in user profile memory
