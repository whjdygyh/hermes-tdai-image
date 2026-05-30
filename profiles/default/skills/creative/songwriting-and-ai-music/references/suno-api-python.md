---
> ⚠️ **⚠️ OUTDATED — `studio-api.suno.ai` SUSPENDED AS OF MAY 2026 ⚠️**
>
> The API backend this library targets (`studio-api.suno.ai`) is dead
> (returns 503 "Service Suspended"). All endpoints below are historical.
> Update this doc when/if Suno relaunches their API or an alternative
> emerges.
>
> **CURRENT STATE: `suno-api` 0.1.0 does NOT work.**
> Use the web interface at `suno.com/create` instead.
---

# suno-api Python Package Reference (Historical)

Package: `suno-api` (PyPI) — Module: `suno`  
Version: 0.1.0  
Dependencies: `curl_cffi` (browser impersonation via curl-impersonate)

**DEPRECATED — DO NOT USE.** The `studio-api.suno.ai` backend has been
suspended. The reference below is kept for diagnostic/historical value
in case Suno re-opens their API.

## Why It No Longer Works

1. `studio-api.suno.ai` (Render.com → Cloudflare) returns **503 "Service Suspended"** — permanent unless Suno re-activates it
2. `clerk.suno.ai` is Cloudflare-protected — returns "DNS points to prohibited IP" for non-browser requests
3. `suno.com/api/*` returns Next.js 404 — the API routes don't exist as HTTP endpoints (embedded in tRPC/JS bundle)
4. `curl_cffi` impersonation fails on systems without patched libcurl (common in WSL, older Linux distros)

## Historical Installation

```bash
pip install suno-api
```

## Historical API Reference

[Content below is preserved for reference only — none of these endpoints currently work.]

### `suno.Suno(cookie: str)`

Main client class. Takes a full Cookie header string from Suno's web app.

```python
from suno import Suno

client = Suno("__session=eyJ...; clerk_active_context=session_...; ...")
```

**Internal flow:**
1. `__init__` calls `_get_sid()` → GET `clerk.suno.ai/v1/client` → extracts `last_active_session_id`
2. First API call triggers `_get_jwt()` → POST `clerk.suno.ai/v1/client/sessions/{sid}/tokens/api` → gets JWT
3. Sets `Authorization: Bearer {jwt}` header
4. On any 401 response → auto-refreshes JWT via `_renew()`

### `client.get_credits() -> int`

Returns `total_credits_left` from Suno billing API.

### `client.songs.generate(prompt, tags, custom, instrumental) -> List[dict]`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `prompt` | str | — | Lyrics (custom mode) or description (standard mode) |
| `tags` | str | `""` | Style/genre tags (required for custom mode) |
| `custom` | bool | `False` | Custom Mode (separate lyrics + tags) |
| `instrumental` | bool | `False` | No vocals |

**Returns:** list of song dicts with `id`, `status`, `audio_url`, `video_url`, etc.

### `client.songs.get(id: str) -> dict`

Get a single song by ID. Poll until `status: "complete"` to get the `audio_url`.

### `client.songs.list() -> List[dict]`

Get the user's entire feed of generated songs.

## Cookie Export Procedure

1. Open `https://suno.com/create` in browser
2. F12 → Network tab
3. Refresh page
4. Find a request containing `__clerk_api_version` in URL
5. Click request → Request Headers → find `Cookie:` line
6. Right-click → Copy value
7. The value is a semicolon-separated string like:
   ```
   __session=eyJ...; clerk_active_context=session_20b47e5b...; suno_device_id=ef026adc-...; statsig_stable_id=2e134466-...; has_logged_in_before=true
   ```

## Historical Endpoints (All Dead)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `https://clerk.suno.ai/v1/client` | 🔴 Cloudflare 403 | "DNS points to prohibited IP" |
| `https://clerk.suno.ai/v1/client/sessions/{sid}/tokens/api` | 🔴 Cloudflare 403 | Same block |
| `https://studio-api.suno.ai/api/generate/v2/` | 🔴 503 Suspended | Render.com backend shut down |
| `https://studio-api.suno.ai/api/feed` | 🔴 503 Suspended | Same |
| `https://studio-api.suno.ai/api/feed/?ids={id}` | 🔴 503 Suspended | Same |
| `https://studio-api.suno.ai/api/billing/info` | 🔴 503 Suspended | Same |
| `https://suno.com/api` | ✅ 200 (SPA) | Returns Next.js app shell, not API docs — useless for automation |
| `https://suno.com/developer` | ✅ 200 (SPA) | Returns Next.js app shell — no developer portal exists |
| `https://suno.com/api/docs` | 🔴 404 | No API documentation |
| `https://suno.com/api/*` (other) | 🔴 404 | Next.js — no HTTP API routes exposed |

## Pitfalls (Historical + New Diagnostics)

1. **`studio-api.suno.ai` suspended** — DNS shows CNAME → `suno-internal-api.onrender.com` → `*.cdn.cloudflare.net`. The origin returns "Service Suspended" from Render. No ETA on restoration.

2. **`curl_cffi` requires patched libcurl** — `impersonate="chrome"` fails with `RequestsError: impersonate chrome is not supported` on systems without curl-impersonate patches. This applies to most WSL environments and many Linux distros. The system libcurl lacks the TLS fingerprinting patches.

3. **`curl_cffi` + proxy causes instant failure** — If `HTTP_PROXY`/`HTTPS_PROXY` env vars are set (e.g., `socks5h://localhost:1080` for V2Ray) but the proxy isn't running, every request fails with `ErrCode: 7 — Connection refused` before even attempting the actual API call. The proxy env vars override everything. **Workaround:** `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY` before running.

4. **Direct `requests` library with JWT** — Using `Authorization: Bearer {jwt}` with Python's `requests` library (not curl_cffi) connects fine to `suno.com` (returns 200) but all API subpaths return 404. The JWT is valid but there's nowhere to send it to. Clerk API (`clerk.suno.ai`) is Cloudflare-blocked from non-browser clients regardless of auth.

5. **Cookie lifespan** — the `__session` JWT expires in ~1 hour (check `exp` claim). Even if the API existed, the `_renew()` flow is Cloudflare-blocked so auto-refresh doesn't work.

6. **hCaptcha** — Suno may throw hCaptcha challenges. The Python library has no solver. If you get 403/429 on generation, the user needs to solve a captcha in their browser.

7. **Song not ready** — `songs.generate()` returns immediately with `id` + status. Must poll `songs.get(id)` until `status == "complete"` before downloading.
