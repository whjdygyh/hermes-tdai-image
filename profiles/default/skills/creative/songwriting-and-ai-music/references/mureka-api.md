# Mureka Native API Reference (2026-05-15)

## Overview
Mureka has a **native REST API** with proper API key authentication. No third-party wrappers needed.

| Item | Value |
|------|-------|
| **API base URL** | `https://api.mureka.cn` |
| **API key portal** | `https://platform.mureka.cn` → "API Keys" tab |
| **API docs** | `https://platform.mureka.cn/docs/` (VitePress SPA) |
| **Auth** | `Authorization: Bearer {api_key}` |
| **Content-Type** | `application/json` |

> ⚠️ **NOT `platform.mureka.cn`** — the API uses `api.mureka.cn` as base. `platform.mureka.cn` is the SPA dashboard/portal.

## Authentication

```bash
curl https://api.mureka.cn/v1/song/generate \
  -H "Authorization: Bearer op_hrcfor6prtizmsrbwdxw5lodmrviw5cbc" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Endpoints

### Song Generation — POST /v1/song/generate
Create a song with custom or auto-generated lyrics.

**Request body:** JSON object
- `lyrics` (string) — lyrics text with metatags like `[Verse]`, `[Chorus]`
- `model` (string) — model version (e.g. `"auto"`, `"mureka-6"`)
- `prompt` (string) — style/genre/mood description

**Response (200):** Async task info
```json
{
  "id": "1436211",
  "created_at": 1677610602,
  "model": "mureka-6",
  "status": "preparing",
  "trace_id": "1e94aba5a2de4cc4bff54a2813c8d36c"
}
```

### Soundtrack Generation — POST /v1/soundtrack/generate
Generate instrumental/soundtrack without vocals.

### Query Task — GET /v1/song/query/{task_id}
Poll async generation status.

**Path param:** `task_id` (string) — from create response

### Lyrics Generation — POST /v1/lyrics/generate
Auto-generate lyrics from a text prompt.

### Lyrics Extension — POST /v1/lyrics/extend
Extend existing lyrics.

### Song Operations
| Endpoint | Description |
|----------|-------------|
| `POST /v1/song/extend` | Continue/extend a song |
| `POST /v1/song/remix` | Remix existing song |
| `POST /v1/song/stem` | Split into stems (vocals, drums, etc.) |
| `POST /v1/song/describe` | AI describes/analyzes a song |
| `POST /v1/song/recognize` | Recognize/identify a song |
| `POST /v1/song/region-edit` | Edit specific region of a song |
| `POST /v1/track/generate` | Generate a single track |

### Vocal Clone — POST /v1/vocal/clone
Clone a voice for song generation.

### TTS
| Endpoint | Description |
|----------|-------------|
| `POST /v1/tts/generate` | Text-to-speech voice generation |
| `POST /v1/tts/podcast` | Create podcast with TTS |

### File Upload (for reference audio)
| Endpoint | Description |
|----------|-------------|
| `POST /v1/uploads/create` | Create upload object |
| `POST /v1/uploads/add` | Append data to upload |
| `POST /v1/uploads/complete` | Finalize upload |

### Billing — GET /v1/account/billing
Check account balance and usage.

## Known Quota Issue (May 2026)
The API key authenticates successfully but returns:
```json
{"error":{"message":"You exceeded your current quota, please check your plan and billing details"}}
```
Needs credits recharged on platform.mureka.cn before generation works.

## Proxy Note (WSL)
Always unset proxy env vars before calling Mureka API:
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
```

## Quick Reference: curl Example
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY

curl -s https://api.mureka.cn/v1/song/generate \
  -H "Authorization: Bearer $MUREKA_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lyrics": "[Verse]\n在暴风雨的夜晚，我独自徘徊\n迷失在雨中，感觉像是被抛弃\n你的回忆，它们在我眼前闪烁\n希望有那么一刻，能找到一些幸福",
    "model": "auto",
    "prompt": "r&b, slow, passionate, male vocal"
  }'
```
