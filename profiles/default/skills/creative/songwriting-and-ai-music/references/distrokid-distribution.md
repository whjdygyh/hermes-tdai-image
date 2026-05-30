# DistroKid Distribution — Cookie Auth & Cloudflare Access

## Overview

DistroKid is used to distribute music to streaming platforms (Spotify, Apple Music, NetEase, Tencent, etc.). It uses Cloudflare protection, making automated access from a server environment very difficult. This doc captures what's known about the auth mechanism and access limitations.

## Cookie Structure

The following cookies are needed for authenticated access to DistroKid:

| Cookie | Domain | HttpOnly | Secure | Purpose | Expires |
|--------|--------|----------|--------|---------|---------|
| **DK_SYN** | distrokid.com | ✅ Yes | ✅ Yes | **Primary auth session token** | Short (~1-2 days) |
| cfid | distrokid.com | ✅ Yes | ❌ | Cloudflare session ID | 6-12 months |
| cftoken | distrokid.com | ✅ Yes | ❌ | Cloudflare session token | 6-12 months |
| __cf_bm | .distrokid.com | ✅ Yes | ✅ Yes | Cloudflare bot management | ~30 min |
| BEEFARONI | .distrokid.com | ❌ | ❌ | User session marker | ~3 days |
| LD_REP_ID | distrokid.com | ❌ | ❌ | User account ID | ~3 days |
| AWSALB* | distrokid.com | ❌ | Varies | AWS load balancer | ~1 day |
| osano_consent* | distrokid.com | ❌ | Varies | GDPR/Cookie consent | 6-12 months |

**DK_SYN is the critical one** — it's the actual auth token. Without it, all other cookies are useless.

## DK_SYN Format

```
A1BD868777F7ACABC7A1A9D6C2A7A3AE969AB28997112563CB18FE2A4DC0B4E6142319FB3EA8F702C94BED31F19C5446-0416612A06F32C232F19044CDDA8BF0B1E4B84EE23B824A3ED941110C53CE616-{timestamp}
```

The value is a hex string with a timestamp suffix: `{hex_hash}-{hex_id}-{timestamp}`. The timestamp is when the session was created.

## Session Expiry

**DistroKid sessions expire quickly.** The DK_SYN cookie typically lasts 1-2 days. After that, the user must log in again from their own browser to get fresh cookies.

## Cloudflare Protection

DistroKid uses **Cloudflare Challenge Platform** (`/cdn-cgi/challenge-platform/`) which:

1. Sets `__cf_bm` cookie on first visit (bot management, ~30 min expiry)
2. Requires JavaScript execution to pass a Turnstile or JS challenge
3. Uses browser fingerprinting (WebDriver detection, canvas fingerprint, etc.)
4. Even headless Chromium with Playwright can be detected

## Access from WSL/Server

**Direct curl/requests: ❌ Blocked by Cloudflare**
- Even with all cookies (DK_SYN, cfid, cftoken, __cf_bm), curl gets Cloudflare challenge page (HTTP 403)
- The `__cf_bm` cookie alone isn't enough — Cloudflare's JS challenge must execute

**Playwright headless Chromium: ❌ Blocked by Cloudflare**
- Can set all cookies via `context.add_cookies()` (must navigate to domain FIRST, then set cookies, then reload)
- DK_SYN gets set correctly ✅
- But Cloudflare still returns challenge page — the JS challenge detects headless mode
- Even anti-detection scripts (`navigator.webdriver` override, plugin spoofing) don't bypass Turnstile

**User's own browser: ✅ The only reliable way**
- User must log in from their own machine (Windows/Mac) with their real browser
- Export cookies via Cookie Editor extension or browser DevTools
- Send the JSON cookie data to the AI assistant
- Cookies work immediately after export (within their expiry window)

## What Each Cookie Does

| Cookie | Without it... |
|--------|--------------|
| DK_SYN | Cannot authenticate — get redirected to login page |
| cfid/cftoken | Cloudflare re-challenges on every request |
| __cf_bm | Cloudflare blocks with JS challenge immediately |
| BEEFARONI | Session state may be reset |
| LD_REP_ID | Account identification lost |
| AWSALB*/AWSALBTG* | Load balancer may route to different backend — session lost |

## Saving Cookies for Future Use

When user exports DistroKid cookies:

1. Save the complete JSON array as a section in 重要记事.md
2. Include all cookies, even seemingly minor ones (AWSALB*, osano*, etc.)
3. Note the export date — cookies expire quickly
4. Format as a Markdown table with columns: domain, name, value (truncated), httpOnly, secure, expires

## Release Status Check (When Accessible)

If you can access DistroKid (via user's browser or fresh cookies):

1. Navigate to `https://distrokid.com/` → should auto-redirect to dashboard
2. Go to `https://distrokid.com/releases/` to see all releases
3. Common statuses: "Processing" → "In Review" → "Approved" → "Live"
4. Each platform has its own timeline: Apple Music (hours-days), Spotify (5+ business days), others (3-7 days)
5. After release, lyrics can be added from the release detail page

## Known Release Flow

1. Upload audio file + cover art + metadata to Distrokid
2. DistroKid reviews (3-5 business days)
3. Distribution to platforms starts after approval
4. Apple Music: fastest (hours to days)
5. Spotify: slowest (5+ business days minimum)
6. NetEase/Tencent (China): varies, can take 1-2 weeks
7. Royalties: DistroKid pays out ~2 months after earnings accrue

## Related

- See `songwriting-and-ai-music` SKILL.md for the full music creation → distribution pipeline
- Suno cookies are managed separately (see 重要记事.md Section 7)
- Artist names: international = Elian Chen, domestic (China) = 陈一
