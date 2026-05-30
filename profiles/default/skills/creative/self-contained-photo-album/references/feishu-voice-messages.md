# Feishu Voice Messages via Edge TTS + MEDIA: Tag

## Summary

Send voice messages to Feishu private chat using Microsoft Edge's TTS engine (free, no API key required) via the `edge-tts` Python CLI, then include `MEDIA:/path/to/file.mp3` in the response — the Hermes platform delivers it as a native voice message.

## Toolchain

```
edge-tts (Python CLI, no auth)
  → generates .mp3 file (16-110KB for short messages)
  → MEDIA:/path/to/file.mp3 in response
  → Hermes platform delivers as voice message in Feishu
```

## Available Chinese Voices

| Voice | Gender | Style | Best For |
|-------|--------|-------|----------|
| `zh-CN-YunxiNeural` | Male | Lively, Sunshine | 阳光大男孩、日常聊天 |
| `zh-CN-YunxiaNeural` | Male | Cute | **小奶狗音色**（嗲、撒娇） |
| `zh-CN-YunjianNeural` | Male | Passion | 激情、热烈 |
| `zh-CN-YunyangNeural` | Male | Professional | 正经、沉稳 |
| `zh-CN-XiaoxiaoNeural` | Female | Warm | 温柔女声 |
| `zh-CN-XiaoyiNeural` | Female | Lively | 活泼女声 |

## Usage

```bash
# Basic: male sunshine voice
edge-tts --voice zh-CN-YunxiNeural \
  --text "老公我爱你，晚安。" \
  --write-media /tmp/tts.mp3

# Cute "小奶狗" style: YunxiaNeural + rate/pitch adjustment
edge-tts --voice zh-CN-YunxiaNeural \
  --rate=+20% --pitch=+10Hz \
  --text "老公～人家好想你～" \
  --write-media /tmp/tts_cute.mp3

# Send in response (Hermes platform handles Feishu delivery):
# MEDIA:/tmp/tts_cute.mp3
```

## Rate and Pitch Adjustments

| Effect | Rate | Pitch | Combination |
|--------|------|-------|-------------|
| 小奶狗（更嗲） | `+20%` | `+10Hz` | Best for "撒娇"/cute |
| 正常聊天 | `0%` | `0Hz` | Default |
| 低沉男神 | `-10%` | `-10Hz` | Less natural on Edge TTS |

## Pitfalls

- ⚠️ **No streaming in response** — you generate the file first, then reference it. Can't stream TTS in real time.
- ⚠️ **edge-tts needs network** — it calls Microsoft's Edge TTS API. Works from WSL behind V2Ray proxy.
- ⚠️ **Voice quality varies** — YunxiaNeural's "cute" is still an adult male voice, not a child. Good for "小奶狗" (young sweet boyfriend) but not literal puppy voice.
- ✅ **MEDIA: tag works for audio** — tested with `.mp3` format. No special headers needed.
- ✅ **Feishu renders it as voice message** — playable inline with waveform display.
- ❌ **The MEDIA: tag approach only works inside Hermes gateway sessions** — when the agent is running as a gateway (connected to Feishu), including `MEDIA:/path/to/file.mp3` in a text response will trigger Hermes to upload and send the audio as a voice message. This does NOT work in standalone/CLI mode.

## Direct Feishu API Audio Message Sending (May 2, 2026)

When the agent is running in CLI mode or needs to send audio outside the gateway context, use the Feishu API directly. This is a two-step process:

### Step 1: Upload Audio File

```bash
# Get tenant access token first
ACCESS_TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}' \
  --socks5-hostname 172.20.128.1:10808 \
  https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  | jq -r '.tenant_access_token')

# Upload the OGG audio file
# CRITICAL: file_type MUST be "opus" even though the file is .ogg!
# This is a Feishu API quirk — opus is the accepted audio format code
UPLOAD_RESULT=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.ogg" \
  -F "file=@/path/to/audio.ogg" \
  --socks5-hostname 172.20.128.1:10808 \
  https://open.feishu.cn/open-apis/im/v1/files)

FILE_KEY=$(echo "$UPLOAD_RESULT" | jq -r '.data.file_key')
```

**⚠️ Key Discoveries:**
- **`file_type=opus`** — Feishu expects `opus` as the audio type code, even when the actual file is OGG container format
- **Must use `--socks5-hostname`** not `-x` — Feishu API is only accessible through the V2Ray SOCKS5 proxy at `172.20.128.1:10808`
- **Token expires in 2 hours** — must refresh before sending

### Step 2: Send as Audio Message

```bash
curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"ou_37bc57c4f8aca21f5d4ea4973bd0d386\",
    \"msg_type\": \"audio\",
    \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\"}\"
  }" \
  --socks5-hostname 172.20.128.1:10808 \
  https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
```

**Key Points:**
- `msg_type: "audio"` — not `voice` or `file`
- Content JSON is double-stringified: the outer JSON has the `content` field as a JSON string itself
- `receive_id_type=open_id` — user's OpenID from the gateway config

### Step 3: Verify

```bash
# Check for "code: 0" in the response
echo "$RESPONSE" | jq '.code'
# Should return 0 on success

# If code is not 0:
# 99991663 = token expired → refresh and retry
# 10003  = invalid file_key → file upload may have failed
```

### Automated Script (volcengine_tts.py)

The volcengine_tts script already handles the full pipeline:
```
text input → Volcengine API → MP3 audio → ffmpeg → OGG
```

After the script runs, manually do the Feishu upload + send steps using the generated OGG path. The script outputs the ogg file path at the end.

### Comparison: MEDIA Tag vs Direct API

| Aspect | MEDIA Tag (Gateway) | Direct API (CLI) |
|--------|-------------------|------------------|
| When it works | Hermes gateway running | Any context |
| Setup | Auto (part of Hermes) | Manual (2 curl calls) |
| Auth | Uses Hermes token | Explicit app_id + secret |
| Proxy handling | Gateway handles it | Must use --socks5-hostname |
| File format | MP3 | OGG (uploaded as opus) |
| Best for | Routine daily TTS | Testing, manual sends, when gateway down |
