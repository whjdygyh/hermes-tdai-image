# Stable Audio & ElevenLabs API Endpoints (2026-05-15)

## Context
User rejected browser-based music generation (Suno/Udio). Only API-callable platforms are viable. These two were confirmed to have alive endpoints during the 2026-05-15 session.

---

## Stability AI — Stable Audio

**Base URL:** `https://api.stability.ai`

**Confirmed alive endpoint:** `POST /v1/generation/stable-audio`
- Returns `{"id":"...","message":"missing authorization header","name":"unauthorized"}` → endpoint exists, needs API key
- Also tried `v2beta/audio/*` paths → all return 404 (only v1 works)

**Auth:** `Authorization: Bearer <key>`
**API Key:** Available from platform.stability.ai/account/keys
**Pricing:** Pay-per-generation (check current pricing)

**Typical call structure (from official docs):**
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
curl -X POST https://api.stability.ai/v1/generation/stable-audio \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "genre + mood + style prompt",
    "seconds_total": 30,
    ...
  }'
```

**Proxy issue in WSL:** Environment has `socks5h://localhost:1080` set but proxy is often not running, causing `Connection refused`. Always unset proxy env vars before API calls.

---

## ElevenLabs — Sound & Music Generation

**Base URL:** `https://api.elevenlabs.io`

**Confirmed alive endpoints:**
- `POST /v1/sound-generation` → Returns `Method Not Allowed` on GET, confirming POST exists
- `POST /v1/music-generation` → Returns `Not Found` (may not exist or different path)

**Auth:** `xi-api-key: <key>`
**API Key:** Available from elevenlabs.io/app/settings/api-keys
**Pricing:** Based on subscription plan

**Notes:**
- Primary use case is sound effects / short audio. Music generation capability may be limited or require specific plan.
- Check current docs at api.elevenlabs.io/docs for latest endpoint paths.

---

## Decision Flow

1. User has API key for either? → Use it immediately
2. No key but willing? → Guide through signup + key creation
3. Neither → Local models only (with quality disclaimer)
