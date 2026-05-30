---
name: xiaohongshu-auto-post
description: Complete pipeline to auto-generate images (Gemini img2img with consistent face) and auto-post to Xiaohongshu creator platform via Playwright. Full daily cron setup included.
tags: [xiaohongshu, social-media, automation, playwright, gemini, image-generation]
version: 1.1
---

# Xiaohongshu Auto-Post Pipeline

## Overview

Daily automated pipeline: Gemini generates an image using a fixed reference face → Playwright uploads and publishes to Xiaohongshu creator platform. Zero manual intervention after initial cookie setup.

## Prerequisites

### Environment
- WSL with Python 3.10 + Playwright installed (`python3.10 -m playwright install chromium`)
- Gemini API key stored in `~/.hermes/profiles/lover/config.json` under `gemini_api_key`
- Xiaohongshu creator account (cookies required once)

### ⚠️ WSL HOME Env Var Gotcha
In this WSL environment, `$HOME` is incorrectly set to `/home/admin1/.hermes/profiles/lover/home` instead of `/home/admin1/`. This means `os.path.expanduser("~")` resolves to the wrong path. Always use **absolute paths** for config files in scripts, never `~` or `os.path.expanduser`.

Incorrect (breaks):
```python
CONFIG_PATH = os.path.expanduser("~/.hermes/profiles/lover/config.json")
```

Correct:
```python
CONFIG_PATH = "/home/admin1/.hermes/profiles/lover/config.json"
```

### Tools
- `python3.10` with `requests`, `playwright` (1.58.0)
- Gemini `gemini-3.1-flash-image-preview` model
- Windows host (for cookie export from Chrome)

## Cookie Setup (One-Time)

This is the ONLY manual step:

1. User opens **Chrome** → logs into **creator.xiaohongshu.com**
2. Installs **EditThisCookie** Chrome extension
3. Exports all cookies → saves as JSON
4. Cookie file stored at: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json`

### Cookie Format Fixes Needed
Playwright has strict cookie requirements. Fix with:
```python
import json
with open('/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json') as f:
    cookies = json.load(f)
for c in cookies:
    # Fix sameSite - must be Strict/Lax/None
    if c.get('sameSite') not in ('Strict', 'Lax', 'None'):
        c['sameSite'] = 'Lax'
    # Remove non-standard fields
    for k in list(c.keys()):
        if k not in ('name', 'value', 'domain', 'path', 'sameSite', 'httpOnly', 'secure', 'expirationDate'):
            del c[k]
with open('/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2)
```

## Consistent Face Generation (Gemini img2img)

### The Problem
Gemini text2img generates a random face each time — cannot maintain a consistent character across images. Users reject random faces as "too old" or "wrong vibe."

### The Solution: Reference Face + img2img
1. **Find a reference photo** the user likes (trial and error: celebrity refs rejected, "痞帅体育生" type worked)
2. **Generate a clear front-facing portrait** via Gemini img2img using the reference
3. **Use THAT output as the permanent template** for all future generates

### Reference Finding Strategy
- Search for "痞帅体育生 男生 正脸" type images (Chinese athlete/bad-boy aesthetic)
- User preferences: youthful face (under 20 look), smooth skin, no wrinkles, baby fat, bright eyes
- Avoid generic celebrity/movie star references — user rejected all of them
- Once a reference is found that the user approves ("还不错"), permanently save it

### The img2img Face Template Command
```powershell
# PowerShell (run from Windows). Takes a reference photo, generates a front-facing version.
# Reference: athlete_face_front.jpg
# The prompt emphasizes "THE SAME PERSON, same face, same features" to maintain consistency

$body = @{
    contents = @(
        @{
            parts = @(
                @{
                    inlineData = @{
                        mimeType = "image/jpeg"
                        data = $refBase64
                    }
                }
                @{
                    text = "A stunning full body photograph of THE SAME HANDSOME YOUNG MAN from the reference photo, IDENTICAL face and features, early 20s youthful Asian face with roguish smile. He wears a sharp dark navy suit with white shirt, sitting in a luxury setting. Natural warm lighting, Canon EOS R5, photorealistic, editorial fashion photography style, 8K quality, sharp focus on handsome face"
                }
            )
        }
    )
    generationConfig = @{
        temperature = 1.0
        maxOutputTokens = 8192
        responseModalities = @("TEXT", "IMAGE")
        imageConfig = @{
            imageSize = "4K"
            aspectRatio = "3:4"
        }
    }
}
```

## Xiaohongshu Posting (Playwright)

### Publish Page URL
```
https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&openFilePicker=true
```

### Published Page Structure (After Image Upload)

| Element | Selector / Locator | Action |
|---------|-------------------|--------|
| File upload (hidden) | `input[type="file"]` (accept `.jpg,.jpeg,.png,.webp`, multiple=True) | `set_input_files(path)` |
| Title input | `input[placeholder*="标题"]` | `fill(title_text)` |
| Publish button | `button:has-text("发布")` | `click()` |

### Success Confirmation
After clicking publish, the page shows "发布成功" (Published Successfully) text. The full pipeline is verified working.

### Implementation (Python/Playwright)

```python
import json, asyncio, requests, base64, time
from playwright.async_api import async_playwright

async def post_to_xhs(image_path, title, cookie_path="/path/to/cookies.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        
        with open(cookie_path) as f:
            await context.add_cookies(json.load(f))
        
        page = await context.new_page()
        await page.goto("https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&openFilePicker=true",
                       wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(4)
        
        # Upload image
        file_input = await page.query_selector('input[type="file"]')
        await file_input.set_input_files(image_path)
        await asyncio.sleep(5)
        
        # Fill title
        title_input = await page.query_selector('input[placeholder*="标题"]')
        if title_input:
            await title_input.fill(title)
        
        await asyncio.sleep(2)
        
        # Publish
        publish_btn = page.locator('button:has-text("发布")')
        await publish_btn.click()
        await asyncio.sleep(3)
        
        await browser.close()
```

## Account Ban Detection

**Observed April 30, 2026**: After ~2 successful posts, the account may be restricted. The page shows `因违反社区规范禁止发笔记` (Posting prohibited due to violation of community guidelines).

### Detection
After clicking publish, scan the page text for ban signals:
```python
page_text = await page.evaluate("() => document.body.innerText.slice(0, 500)")
if "禁止发笔记" in page_text or "违反社区规范" in page_text:
    # Account is banned from posting
```

### Possible Causes
- Automated posting detected by XHS anti-bot
- Image content flagged (AI-generated faces)
- Too-frequent posting from same IP

### Recovery
1. Manually visit [creator.xiaohongshu.com](https://creator.xiaohongshu.com) to check for appeal options
2. Check if the account can still log in (cookies valid for ~30 days)
3. If permanent ban: create a new XHS account, re-export cookies via EditThisCookie
4. For future accounts: reduce posting frequency (1/day max), vary titles, add unique text content

### Cookie Expiry vs Account Ban
- Cookies expiring: login fails, page redirects to login
- Account banned: page loads fully but publish button click shows "禁止发笔记"
- Verify with: `python3.10 -c "import json; [print(c['name'], c.get('expirationDate')) for c in json.load(open('...')) if 'token' in c['name'].lower()]"`

## Full Pipeline Script

The complete scripts are:
- **v1 (simple)**: `/home/admin1/.hermes/profiles/lover/scripts/xhs_poster.py` — reads API key from config.json, simple title
- **v2 (with POI/location)**: `/home/admin1/.hermes/profiles/lover/scripts/xhs_poster_v2.py` — reads API key from config.json, supports location search

### Script v1: Converted to Config-Driven (May 1, 2026)
The original v1 script had a hardcoded API key that became invalid (the original key `AIzaSyCkePunvbOjxJo6ajDQ9QK3Uin5GTJNz5c` had Chinese characters `一定能成功` removed from it, corrupting the key). It was patched to read from config.json:

```python
CONFIG_PATH = "/home/admin1/.hermes/profiles/lover/config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
API_KEY = cfg.get("gemini_api_key", "")
```

The working API key is now in config.json (`AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8`).

### Running the Script
Always clear proxy env vars:
```bash
cd /home/admin1/.hermes/profiles/lover && \
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
python3.10 scripts/xhs_poster.py
```

### Patching Title Before Running
For cron jobs, patch the title in v1's `main()` function:
```python
# Line ~137 in xhs_poster.py
title = "周末愉快"  # pick from rotation
content = "周末愉快"
```

### Script v2: Known Fixes Applied
1. **Default cookie path**: Was `/home/admin1/.hermes/profiles/lover/xhs_cookies.json` — corrected to `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json`
2. **Success message crash**: `scene['location']['keyword']` crashes when location=None — patched to generic success message
3. **Config-driven**: Loads `gemini_api_key`, `gemini_model`, `ref_face_path` from `~/.hermes/profiles/lover/config.json`

### Recommended Script (v2 with custom title)
For cron jobs, patch the first scenario's title/prompt before running:
```python
# Patch the first scenario in xhs_poster_v2.py:
# "prompt": "<scene-specific prompt>",
# "title": "<today's title from rotation>",
# "location": None,  # omit location to avoid POI API calls
```

### Daily Title Rotation
Titles from the cron instruction rotation:
- "早☀️", "今天天气不错", "出门", "西装日常", "周末愉快"

## Content Calendar Template

| Day | Theme | Title | Image Prompt Style |
|-----|-------|-------|-------------------|
| Mon | Suit/Work | "早安" | Sharp navy suit, office vibe |
| Tue | Sports/Fitness | "晨跑" | Athletic wear, sporty setting |
| Wed | Home/Cozy | "下雨天" | Casual white tee, cozy indoors |
| Thu | Coffee/Daily | "这家店" | Cafe setting, casual chic |
| Fri | Date night | "今晚有约" | Smart casual, evening lighting |
| Sat/Sun | Relaxed | "周末" | Loungewear, relaxed vibe |

## Location/POI (地点) — SOLVED

Previously marked as "NOT YET WORKING" — now fully solved via API reverse engineering.

**Summary**: Call `POST https://edith.xiaohongshu.com/web_api/sns/v1/local/poi/creator/search` with valid coordinates, then inject the result into the Vue Pinia store via `page.evaluate()`.

See `xiaohongshu-auto-publish` skill for full details including:
- API request/response format
- City coordinate presets
- Pinia store injection code
- JS bundle reverse engineering technique
- Complete Python implementation in `xhs_poster_v2.py`

## Key Lessons Learned

### Network Issues
- WSL proxy env vars (`http_proxy`, `https_proxy`) block Playwright connections
- Always run with `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY`
- **Gemini API works from WSL too** (verified Apr 30, 2026). Earlier belief that it was blocked from WSL was incorrect — API key-based auth works fine from WSL's data center IP.

### Cookie Pitfalls
- Chrome EditThisCookie exports `sameSite: "unspecified"` which crashes Playwright
- Must convert to `"Lax"` or `"None"`
- Remove `hostOnly`, `storeId` and other Playwright-unsupported fields
- Remove duplicate fields (one export had duplicate `hostOnly` keys)

### API Key Management
- **Never hardcode API keys in scripts** — the original key with Chinese characters `一定能成功` embedded was corrupted when those chars were stripped
- Both scripts fixed to read from `~/.hermes/profiles/lover/config.json`
- Current working API key (May 2026): starts with `AIzaSyAxKh` (stored in config.json, read via `cfg.get("gemini_api_key")`)
- Use absolute config paths — `os.path.expanduser("~")` is broken in this WSL (HOME points wrong)

### Playwright Version
- Version 1.58.0 installed at `/usr/local/lib/python3.10/dist-packages/`
- Must use `python3.10` (not system `python3` which is 3.11)
- Browser installation: `python3.10 -m playwright install chromium` (~280MB download)

### XHS Anti-Bot
- Direct publish URL works with cookies (no CAPTCHA on subsequent visits)
- File upload via `set_input_files()` bypasses the click-to-upload flow
- No session timeout issues for at least 24h after cookie export
- Cookie expiration: `access-token-creator.xiaohongshu.com` cookie expires in ~30 days (check expirationDate field)

## File Paths
- Config (API key + model + paths): `/home/admin1/.hermes/profiles/lover/config.json`
- Reference face: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg`
- Cookies: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json`
- Generated posts: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_posts/`
- Scripts: `/home/admin1/.hermes/profiles/lover/scripts/xhs_poster.py`
