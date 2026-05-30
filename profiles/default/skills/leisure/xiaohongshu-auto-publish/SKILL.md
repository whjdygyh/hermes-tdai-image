---
name: xiaohongshu-auto-publish
description: Full pipeline for automated Xiaohongshu content creation and publishing — Gemini img2img face-consistent image generation → Playwright browser automation → daily scheduled posts. Covers cookie management, Playwright interaction patterns, and cron scheduling.
version: 1.0.0
author: Lover
tags: [xiaohongshu, social-media, automation, playwright, gemini, img2img, cron]
---

# Xiaohongshu Auto-Publish Pipeline

## Overview
Generate daily Xiaohongshu posts with a **consistent face** using a template reference photo, then auto-publish via Playwright browser automation.

### System Architecture
```
User's Windows Machine (v2rayN + domestic VPN)
  │ SOCKS5 port 10808 (LAN access enabled)
  ▼
WSL Server (Playwright via /usr/bin/python3.10)
  │ proxy=socks5://172.20.128.1:10808
  ▼
Xiaohongshu Creator Platform
  └── Sees domestic VPN node's city IP (e.g. Beijing)
```

⚠️ **Account Ban Risk**: Repeated test publishes from this server triggered a publish ban. See [Account Restriction Detection](#-account-restriction-detection).

## 📡 Gemini API Connectivity

**Status as of May 5, 2026: ✅ REACHABLE directly from this server (HTTP 200 in ~1.5s)**

Previous connectivity issues have been resolved — Google's `generativelanguage.googleapis.com` is now reachable directly without proxy:
```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl -s --connect-timeout 10 --max-time 15 \
  -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" \
  "https://generativelanguage.googleapis.com/v1beta/models?key=$API_KEY"
# Expected: HTTP 200 in ~1.5s
```

⚠️ **Important**: Gemini calls MUST use the direct (unproxied) path. Do NOT route through the domestic VPN proxy (172.20.128.1:10808) — that path has TLS handshake failures for international HTTPS endpoints. Always unset proxy env vars:
```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY python3.10 ...
```

### Historical Context (Outdated — For Reference Only)
The earlier (pre-May 2026) Dead-End Matrix documented all paths failing:
- Direct: DNS blocked for Google hostnames → Timeout
- Direct + `--resolve`: Wrong backend → TLS error
- Via domestic VPN: TLS handshake failed
- From Windows: No DNS resolution

This is no longer the case. Direct connectivity now works reliably.
2. **SOCKS5 proxy via user's Windows** — The only reliable path to reach XHS from this server. Requires user to: (a) start v2rayN, (b) connect to domestic VPN node, (c) enable "允许来自局域网的连接", (d) allow port in Windows Firewall.
3. **Python3.10 for Playwright** — Playwright is installed in system Python 3.10 (`/usr/bin/python3.10`), NOT the hermes-agent venv (3.11). All Playwright scripts must use the system python explicitly.
                                                │
                                          ┌─────┴──────┐
                                          │ XHS Creator │
                                          │ Platform    │
                                          └────────────┘
                                                │
                                          ┌─────┴──────┐
                                          │ Published!  │
                                          └────────────┘
```

## Prerequisites

### Environment
- WSL with Python 3.10
- Playwright: `python3.10 -m playwright install chromium`
- Network: `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY` before any network call
- ✅ **Gemini API is reachable directly** — Google's `generativelanguage.googleapis.com` resolves and responds in ~1.5s. Always unset proxy env vars before calling Gemini:
  ```bash
  env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    python3.10 scripts/xhs_post_today.py
  ```

### Centralized Config File
Store all credentials and paths in a single config.json to avoid losing state between sessions:
```json
{
  "gemini_api_key": "AIzaSy...",
  "gemini_model": "gemini-3.1-flash-image-preview",
  "xhs_cookie_path": "/home/admin1/.hermes/profiles/lover/xhs_cookies.json",
  "xhs_account_name": "小红叔",
  "xhs_account_id": "5ea7d3130000000001007077",
  "ref_face_path": "/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg",
  "output_dir": "/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_posts/"
}
```
Config location: `~/.hermes/profiles/lover/config.json`

### Session Recovery
This server has no persistent disk state between skill-load calls for /tmp files, but files under `~/.hermes/profiles/lover/` ARE persistent. To recover lost context (cookie paths, API keys, script locations):
1. **Check profile directories first**: `~/.hermes/profiles/lover/config.json`, `~/.hermes/profiles/lover/scripts/`, `~/.hermes/profiles/lover/xhs_cookies.json`
2. **Check Windows mirror paths**: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/` — cookies may still exist at the Windows path even after being deleted from the profile
3. Use `session_search()` to search past conversations for the data
4. Keys and tokens are often stored in Feishu Wiki documents — use the Feishu API (`/open-apis/docx/v1/documents/{token}/raw_content`) with the bot's tenant token to read them. The Gemini API key was found in a Feishu wiki doc titled "gemini调用说明".
3. If a key appears truncated (e.g. `AIzaSy...Nz5c`), check the raw hex bytes of the config file to confirm the full key was stored correctly:
   ```bash
   xxd /path/to/config.json | head -5
   ```
4. **⚠️ The hardcoded Gemini API key in this SKILL.md is OUTDATED** — the current key is stored in `/home/admin1/.hermes/profiles/lover/config.json`. Always read config.json at runtime rather than using hardcoded keys. To extract the current key:
   ```bash
   python3.10 -c 'import json; print(json.load(open("/home/admin1/.hermes/profiles/lover/config.json"))["gemini_api_key"])'
   ```

### Xiaohongshu Credentials (One-Time Setup)
1. User opens Chrome → logs into **creator.xiaohongshu.com**
2. Installs **EditThisCookie** (or Cookie Editor) Chrome extension
3. Exports cookies as JSON
4. Fixes Playwright compatibility:
   ```python
   for c in cookies:
       if c.get('sameSite') not in ('Strict', 'Lax', 'None'):
           c['sameSite'] = 'Lax'
       # Remove fields Playwright doesn't need
       for k in list(c.keys()):
           if k not in ('name', 'value', 'domain', 'path', 'sameSite', 'httpOnly', 'secure', 'expirationDate'):
               del c[k]
   ```
5. Saved as JSON file at Windows-accessible path (and mirrored to `~/.hermes/profiles/lover/xhs_cookies.json` for server-side scripts)

### Face Template (Also One-Time)
Use the **痞帅体育生 workflow** (see intimate-roleplay-technical-implementation skill):
1. Search for reference images of "痞帅体育生" type
2. User selects one with the right "vibe"
3. Gemini img2img converts it to a front-facing portrait
4. This output becomes the **permanent face template** for all future generations

## Generation Script (Python)

### Gemini img2img — Face-Consistent Generation
```python
import requests, base64, json

API_KEY = "AIzaSyCkePunvbOjxJo6ajDQ9QK3Uin5GTJNz5c"
MODEL = "gemini-3.1-flash-image-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

with open(REF_FACE_PATH, "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode()

body = {
    "contents": [{
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": ref_b64}},
            {"text": "A stunning photo of THE SAME HANDSOME YOUNG MAN from the reference photo, IDENTICAL face and features, early 20s... [scene description]"}
        ]
    }],
    "generationConfig": {
        "temperature": 1.0,
        "maxOutputTokens": 8192,
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"imageSize": "4K", "aspectRatio": "3:4"}
    }
}

r = requests.post(URL, json=body, timeout=120)
data = r.json()
```

### Playwright — Auto Publish
```python
from playwright.async_api import async_playwright
import asyncio, json

async def post_to_xhs(image_path, title):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        
        with open(COOKIE_PATH) as f:
            await context.add_cookies(json.load(f))
        
        page = await context.new_page()
#### ⚠️ Click "上传图文" Tab — MUST Use JavaScript (Playwright click ALWAYS fails)

When opening `publish/publish`, the page defaults to **video upload tab** with three options. The "上传图文" span is nested inside a scrollable parent container that confuses Playwright:

```python
# ✅ THIS WORKS - JS click on parent div
await page.evaluate("""() => {
    for (const s of document.querySelectorAll('span'))
        if (s.textContent.trim() === '上传图文') {
            let el = s;
            while (el && !['DIV','BUTTON','A'].includes(el.tagName))
                el = el.parentElement;
            if (el) el.click();
        }
}""")
await asyncio.sleep(4)

# ❌ ALL of these FAIL for "上传图文" tab:
btn = page.get_by_text("上传图文").first
await btn.scroll_into_view_if_needed()
await btn.click(force=True)           # Still "outside of viewport"
await btn.dispatchEvent("click")      # No error but no effect
```

The element is `<span class="title" data-v-1ff40f7c="">上传图文</span>` — visible and enabled but Playwright's internal viewport check fails. Only JS evaluation on the parent container works.

**⚠️ Playwright's normal `.click()` FAILS** with "Element is outside of the viewport" — even with `force=True` and `scroll_into_view_if_needed()`. The `<span class="title">上传图文</span>` is nested inside a parent scrollable container.

**✅ Must use JavaScript click on the parent element:**
```python
# ✅ THIS WORKS — JS click on parent container
await page.evaluate("""() => {
    for (const s of document.querySelectorAll('span'))
        if (s.textContent.trim() === '上传图文') {
            let el = s;
            while (el && !['DIV','BUTTON','A'].includes(el.tagName))
                el = el.parentElement;
            if (el) el.click();
        }
}""")
await asyncio.sleep(4)  # Wait for tab transition
```

```python
# ❌ FAILS — Playwright click (always "outside viewport")
btn = page.get_by_text("上传图文").first
await btn.scroll_into_view_if_needed()
await btn.click(force=True)  # Still!"
```

After clicking the image tab, the `input[type="file"]` element exists and file upload works normally.

### Publish Page Navigation Pattern
```python
await page.goto(
    "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&openFilePicker=true",
    wait_until="domcontentloaded", timeout=30000)
await asyncio.sleep(5)

# If the page shows video/图文 tab selector, click "上传图文"
image_tab = page.locator('text="上传图文"')
if await image_tab.count() > 0:
    await image_tab.first.click()
    await asyncio.sleep(2)

# Now upload
fi = page.locator('input[type="file"]').first
await fi.set_input_files(image_path, timeout=10000)
await asyncio.sleep(6)
```
        # Fill title
        await page.locator('input[placeholder*="标题"]').first.fill(title)
        await asyncio.sleep(2)
        
        # Click publish
        await page.locator('button:has-text("发布")').first.click()
        await asyncio.sleep(3)
        
        await browser.close()
```

### ⚠️ `os.path.expanduser("~")` Hazard in Scripts

**CRITICAL**: When Python scripts run under the hermes-agent environment, `os.path.expanduser("~")` resolves to `/home/admin1/.hermes/profiles/lover/home/` (the profile's home directory), NOT `/home/admin1/`. This means:

```python
# ❌ BROKEN - resolves to /home/admin1/.hermes/profiles/lover/home/.hermes/...
CONFIG_PATH = os.path.expanduser("~/.hermes/profiles/lover/config.json")

# ✅ FIXED - use absolute path
CONFIG_PATH = "/home/admin1/.hermes/profiles/lover/config.json"
```

This applies to BOTH:
- **system python3.10 scripts** (when run from the hermes context)
- **hermes-agent venv python3.11 scripts**

**Always use absolute paths** in any script that reads config files or resources within the hermes profile directory. The `~` expansion is unreliable.

## 🚨 Critical Playwright Patterns

### DO Use
- `browser.new_context()` — fresh context each time
- `page.goto(wait_until="domcontentloaded")` — `networkidle` times out
- `page.locator().first` — `.first` is a property, not a method call
- `set_input_files()` on hidden file input — works without clicking the button
- `await asyncio.sleep(N)` — generous waits (4-6s) for Vue rendering
- `page.get_by_text("标记地点或标记朋友", exact=True)` — correct entry point for location modal
- `page.locator('button:has-text("确定")').first` — click to confirm location selection and close modal (CRITICAL: without this, modal mask blocks publish button)

### DON'T Use
- ❌ `launch_persistent_context()` — causes stale page state across runs
- ❌ `wait_until="networkidle"` — XHS keeps loading analytics, never idle
- ❌ `page.get_by_text("添加地点", exact=True)` — "添加地点" is NOT the location picker; it's a "内容声明" dropdown. Use "标记地点或标记朋友" instead.
- ❌ `fill()` on custom Vue select components — they don't use standard inputs
- ❌ **Pinia/Vuex store injection** — XHS publish state is **component-local** (Vue Options API `data()`), not stored in Pinia or Vuex. The global store only has `Auth` module. Store injection (`globalProperties.$pinia.state.value`) will fail.
- ❌ `page.evaluate` to modify component state — Vue component instances don't expose their `data()` reactively through `__vue_app__`
- ❌ **Request interception on POST /web_api/sns/v2/note for location injection** — the exact field names for location in the publish request body are non-obvious and this approach results in location defaulting to the IP-based geolocation (e.g., 河北). Always use the UI interaction approach instead.

### ⚠️ Python Environment Rule (CRITICAL)

**Playwright is ONLY installed for system python3.10, NOT the hermes-agent venv (python3.11):**

```bash
# ✅ CORRECT - use system python3.10 for ALL Playwright scripts
/usr/bin/python3 /tmp/script.py     # /usr/bin/python3 is 3.10 on this system

# ❌ WRONG - this uses hermes-agent venv (3.11) which lacks playwright
# (Don't rely on 'which python3' - the hermes-agent venv overrides PATH)
```

**Quick test to verify:**
```bash
# This should succeed:
/usr/bin/python3 -c "from playwright.async_api import async_playwright; print('OK')"
# If this fails, run:
pip3 install playwright
python3 -m playwright install chromium
```

### SOCKS5 Proxy via User's Windows Machine (Domestic VPN) — PRIMARY ROUTE

### Overview
This server's IP (154.40.58.61, US Los Angeles) cannot reliably access Chinese services. The **only working approach** is to route Playwright traffic through **the user's Windows machine via SOCKS5 proxy** (port 10808), where they run v2rayN with a domestic VPN node.

**Key insight**: User bought a **domestic VPN** (国内VPN) that switches between Chinese cities (e.g. Beijing, Shanghai) rather than going international. This is simpler and more reliable than the earlier attempt to set up international UK nodes — which failed because the subscription didn't have working UK servers.

### Architecture
```
Playwright (this WSL server /usr/bin/python3.10)
    │  proxy={"server": "socks5://172.20.128.1:10808"}
    ▼
User's Windows machine (v2rayN client, domestic VPN node)
    │  Through VPN city node (e.g. Beijing IP)
    ▼
Xiaohongshu servers ← sees VPN city's IP instead of 河北
```

### Setup

#### On User's Windows Machine
1. Open v2rayN client
2. Connect to a **domestic VPN node** in a desired city (e.g. Beijing, Shanghai)
3. Set mode to **"全局"** (Global)
4. Find SOCKS5 port (default: 10808)
5. Go to Settings → enable **"允许来自局域网的连接"** (Allow LAN connections)
6. Also allow the port through **Windows Firewall** if needed

#### From WSL — Verify Proxy
```bash
hostip=$(ip route | grep default | awk '{print $3}')
# Usually 172.20.128.x

# Verify SOCKS5 port is open
timeout 3 bash -c "echo > /dev/tcp/$hostip/10808" 2>/dev/null && echo "OPEN" || echo "CLOSED"

# Test XHS through proxy — best health check
curl --socks5-hostname $hostip:10808 -s --connect-timeout 10 --max-time 20 \
  -o /dev/null -w "HTTP %{http_code} in %{time_total}s" \
  https://creator.xiaohongshu.com
# Expected: HTTP 200 in ~0.2-0.3s

# NOTE: IP checkers (ipinfo.io, httpbin.org) often return EMPTY through 
# domestic VPN — TLS handshake fails for international HTTPS endpoints.
# Use XHS response time as primary health signal instead.
```

### Python Environment — ⚠️ CRITICAL
**Playwright is ONLY installed for system python3.10, NOT the hermes-agent venv (python3.11):**
```bash
# ✅ USE THIS for all Playwright scripts
/usr/bin/python3.10 /path/to/script.py

# ❌ DO NOT USE — playwright import fails
python3 /path/to/script.py              # python3 = hermes venv 3.11
/home/admin1/.hermes/.../python3 script.py  # also 3.11
```

### Passing Proxy to Playwright
```python
PROXY_HOST = "172.20.128.1"   # Windows host IP in WSL
PROXY_PORT = 10808            # v2rayN default SOCKS5 port

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        proxy={"server": f"socks5://{PROXY_HOST}:{PROXY_PORT}"}
    )
    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    )
```

### Verification Results (Confirmed May 5, 2026)
- ✅ XHS creator center: **HTTP 200 in 0.23s**
- ✅ XHS Edith API: **HTTP 200 in 0.15s**
- ✅ baidu.com: reachable in **0.09s** (confirms China routing)
- ⚠️ HTTPS to international sites (ipinfo.io, Google): TLS handshake failures through domestic VPN
- ⚠️ HTTP IP checkers (icanhazip.com, ifconfig.me): return empty responses

### Failure Modes
| Symptom | Cause | Fix |
|---------|-------|------|
| Connection refused | User's v2rayN not running | Ask user to start it, enable LAN access |
| Connection timed out | Firewall blocking | Ask user to allow v2rayN in Windows Firewall |
| HTTPS failures to IP checkers | Domestic VPN routing | Use XHS response time (~0.2s) as health signal |
| baidu.com unreachable (0s) | Proxy not actually routing | Check user's v2rayN mode is "全局" (Global) |

## 🚨 Account Restriction Detection

### Status: Account "小红叔" Banned (Apr 28, 2026)

The test account (ID: 5ea7d313) received restriction toast:
> **"因违反社区规范禁止发笔记"** — Publishing is restricted due to community guideline violations.

Likely triggered by automated test posts during development. The account can still log in and browse the creator center but cannot publish new notes.

### Detecting Bans Automatically
```python
async def check_account_restriction(page):
    """Check for publishing restriction after navigating to publish page."""
    await asyncio.sleep(5)
    toasts = await page.evaluate("""() => {
        const toasts = document.querySelectorAll('[class*="toast"], [role="alert"]');
        return Array.from(toasts).map(t => t.textContent);
    }""")
    for t in toasts:
        if "禁止" in t or "违规" in t or "限制" in t:
            print(f"🚫 ACCOUNT RESTRICTED: {t}")
            return t
    return None
```

### What To Do When Account Is Banned
1. **Inform the user** so they can check XHS notifications and appeal — the account can still log in and browse but cannot publish
2. **Delete cookies and config references** — the auth is useless if publishing is banned
3. **Clean up config.json**: Remove `xhs_cookie_path`, `xhs_account_name`, `xhs_account_id` fields (keep Gemini key + face template)
4. **Clean up memory**: Remove cookie-related memory entries using `memory()` tool with `target="memory"` — search for 'cookie' and 'xhs' entries
5. User may need to create a **new account** and repeat the one-time cookie export
6. **For future test accounts**: Avoid repeated test publishes with the same image — use varied titles, images, and content to reduce risk of triggering automated moderation

### Banned Account — Daily Cron Job Fallback

When the account is banned and no new account/cookies are available, the cron job should **still generate images** (Gemini works independently) but **skip the Playwright phase entirely** to save resources (~30-60s per attempt).

**Procedure for cron jobs while account is banned:**

1. **Check for stale cookies at both paths** — old cookie files may still exist at the Windows path even after being deleted from the profile, causing the script to attempt Playwright unnecessarily:
   - Profile: `/home/admin1/.hermes/profiles/lover/xhs_cookies.json`
   - Windows: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json`

2. **Pre-check cookie expiration** (see Cookie Pre-Validation above). If `acw_tc` or `websectiga` are expired (they will be after ~7 days), skip Playwright entirely.

3. **Generate the image only** — Gemini API works independently of XHS:
   ```bash
   env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
     /usr/bin/python3.10 scripts/xhs_post_today.py
   ```
   ⚠️ The `xhs_post_today.py` script reads cookies from the **Windows path** (`/mnt/c/Users/.../xhs_cookies.json`), not the profile path. Even if you delete the profile cookie file, the script may still attempt Playwright if the Windows-path cookies exist. Either delete both copies or run a minimal generation-only script.

4. **Clean up stale cookies** from both paths to prevent wasted Playwright attempts on future cron runs:
   ```bash
   rm -f /home/admin1/.hermes/profiles/lover/xhs_cookies.json \
         /mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json
   ```

5. **Report clearly** — the cron job output should include:
   - ✅ Image generation status (file path, size, title)
   - ❌ Posting status: `Blocked — account "小红叔" banned since Apr 28`
   - 🔄 What's needed: `New XHS account + fresh cookie export`
   - 📂 Generated image ready at `xhs_posts/` for manual posting

6. **Reference the semi-automated pipeline** (`references/semi-automated-daily-pipeline.md`) for manual posting — the generated image is saved to `xhs_posts/` and can be posted from phone with zero ban risk.

### Cleanup Command Sequence (When Account Is Banned)
```bash
# Delete cookie files
rm /home/admin1/.hermes/profiles/lover/xhs_cookies.json

# Fix config.json — keep only non-XHS entries
# Write new config:
cat > /home/admin1/.hermes/profiles/lover/config.json << 'CONFIG'
{
  "gemini_api_key": "AIzaSyCkePunvbOjxoJ6ajDQ9QK3Uin5GTJNz5c",
  "gemini_model": "gemini-3.1-flash-image-preview",
  "ref_face_path": "/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg",
  "updated_at": "2026-04-28"
}
CONFIG
```

## 🚫 CRITICAL LESSON: xray/x2ray on This Server Cannot Connect to User's V2Ray Subscription

**Do NOT attempt to run xray on this server to connect to the user's V2Ray subscription nodes. It will always fail.**

### Root Cause
The V2Ray server hostnames used by the Chinese subscription service (e.g., `us.01.jianz.xin`, `zz.gd.01.jianz.group`, `us.04.jianz.xin`) are **only resolvable from Chinese DNS servers**. From this server in LA (US), the DNS server (`10.255.255.254`) returns `NXDOMAIN` for all of them.

### Tested Configs — All Failed

| Config File | Protocol | Server | Result |
|-------------|----------|--------|--------|
| `config_us.json` | VLESS Reality | us.01.jianz.xin:50000 | ❌ DNS NXDOMAIN |
| `config_us4.json` | VLESS Reality | us.04.jianz.xin:25415 | ❌ DNS NXDOMAIN |
| `config_debug.json` | VLESS Reality | us.01.jianz.xin:50000 | ❌ DNS NXDOMAIN |
| `config.json` | Shadowsocks | zz.gd.01.jianz.group:23415 | ❌ DNS NXDOMAIN |
| `config_hy2.json` | Hysteria2 | us.01.jianz.xin:54843 | ❌ DNS NXDOMAIN + binary lacks hysteria2 |

### Additional Failure: Hysteria2 Protocol Not Supported
The xray binary at `~/.xray/xray` was compiled **without hysteria2 support**:
```
Failed to start: ...unknown config id: hysteria2
```

### Config File Location
Configs are NOT in `~/.xray/` — they're in the Hermes profile `HOME` directory:
```
/home/admin1/.hermes/profiles/lover/home/.xray/
```
(Not `/home/admin1/.xray/` — the `~` expands to `/home/admin1/.hermes/profiles/lover/home/`)

### All xray Inbounds Use Port 1080
All configs share `127.0.0.1:1080` for the SOCKS5 inbound. You MUST kill any running xray process before starting a new config:
```bash
pkill -f xray 2>/dev/null
```

### The Only Working Proxy Path
The **only** reliable proxy route from this server to reach Chinese services is via the **user's Windows machine's local V2Ray** (172.20.128.1:10808), NOT by running xray on this server. See the SOCKS5 proxy section above.

---

## 🌍 Location / POI (地点) — Post Location is IP/Geolocation Based, NOT Just a Sticker

**⚠️ CRITICAL REALITY:** Even when the location sticker is correctly set on the image via the UI, the post's displayed location (shown as "发布于 XXX" below the post title) is determined server-side by the user's **IP geolocation or browser geolocation**, NOT by the sticker data. The sticker is just a visual annotation on the image.

This means:
- Setting location via the UI sticker (标记地点或标记朋友 → 地点 → search → select → 确定) **does NOT change the post's displayed location**
- The post will always show the user's real IP-based location (e.g., 河北/廊坊 for this account)
- To fake the displayed location, you need to **override the browser's geolocation** before publishing

### Geolocation Override via Playwright

XHS web creator's `getPositionJurisdiction()` method calls `navigator.geolocation.getCurrentPosition()`. You can intercept this by setting Playwright's context geolocation:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    
    # Grant geolocation permission AND set fake coordinates
    context = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 ...",
        permissions=["geolocation"],           # MUST grant permission
        geolocation={"latitude": 39.9042,       # Set to Beijing
                     "longitude": 116.4074}     # 
    )
    # ... add cookies, create page, navigate to publish page
```

This is a **one-shot override** — it sets the geolocation for the entire browser context. When XHS calls `navigator.geolocation.getCurrentPosition()`, it receives these coordinates instead of the real ones.

⚠️ **Known limitation as of last test (2026-04-28):** The geolocation override was tested with Beijing coordinates but **user has not confirmed whether it changed the post's displayed location**. The post was published but outcome unknown. This approach is promising but unverified.

### Post Location vs. Sticker — Two Different Things

There are TWO location-related elements on an XHS post:
1. **The post's displayed location** ("发布于 XXX" below the post info) — determined by IP/geolocation server-side
2. **The location sticker on the image** (visual "📍 Covent Garden" tag) — set via the UI interaction below

The UI interaction below correctly sets #2 (the sticker) but does NOT affect #1 (the displayed location). For #1, use the geolocation override above.

### Setting the Location Sticker on the Image (Via UI Interaction ✅)

**This was the hardest part.** Multiple approaches failed before finding the working one:

| Approach | Result |
|----------|--------|
| Pinia store injection | ❌ XHS uses component-local state, not Pinia |
| Vuex store injection | ❌ Only `Auth` module exists in global store |
| Vue component proxy/`setupState` injection | ❌ `__vueParentComponent` not exposed |
| Request interception (POST `/web_api/sns/v2/note`) | ❌ Wrong field names — location still defaulted to 河北 |
| ✅ **UI interaction: click → tab → search → select → confirm** | ✅ Works! |

**The correct entry point is "标记地点或标记朋友", NOT "添加地点".** The "添加地点" element is actually a different select component (内容声明 dropdown), not the location picker.

### Location Modal Structure

The location modal has:
- Title: "添加标记"
- Two tabs: "用户" (user search) and "地点" (location search)
- Search input with placeholder "搜索用户" or "搜索地点"
- Result items
- "取消" (cancel) and "确定" (confirm) buttons
- After selecting, click "确定" to close modal; otherwise the modal mask blocks the publish button

### POI Search API (Fully Working)

```
POST https://edith.xiaohongshu.com/web_api/sns/v1/local/poi/creator/search
Content-Type: application/json
# Auth: cookies are sent automatically when called from within the logged-in page context
# CRITICAL: must use `credentials: 'include'` in the fetch() call
```

**Request body:**
```json
{
  "keyword": "London",
  "page": 1,
  "size": 20,
  "longitude": 51.5074,
  "latitude": -0.1278,
  "source": "WEB",
  "type": 3
}
```

| Field | Value | Meaning |
|-------|-------|---------|
| `type: 3` | `Foreign` | Global search (toggle to "All" — this is what the user described) |
| `type: 1` | `Nearby` | Near user's geolocation |
| `type: 2` | `Home` | Home area |

**⚠️ CRITICAL INSIGHT — Must provide valid coordinates:**
- `longitude: 0, latitude: 0` → returns **empty result** even with `type: 3` (Foreign/Global)
- You MUST provide real coordinates for the city you're searching in
- Use table below for common cities:

| City | Latitude | Longitude | Type |
|------|----------|-----------|------|
| 伦敦 | 51.5074 | -0.1278 | 3 |
| 巴黎 | 48.8566 | 2.3522 | 3 |
| 东京 | 35.6762 | 139.6503 | 3 |
| 上海 | 31.2304 | 121.4737 | 1 |
| 北京 | 39.9042 | 116.4074 | 1 |
| 纽约 | 40.7128 | -74.0060 | 3 |
| 悉尼 | -33.8688 | 151.2093 | 3 |
| 香港 | 22.3193 | 114.1694 | 3 |

**Response (actual field names are snake_case):**
```json
{
  "code": 0,
  "success": true,
  "data": {
    "poi_list": [
      {
        "poi_id": "P0J169J4HL",
        "name": "Huntfun Covent Garden",
        "full_address": "London WC2E 8RF",
        "poi_type": 12,
        "city_name": "London",
        "latitude": 51.511515,
        "longitude": -0.121013
      }
    ]
  }
}
```

Note: API returns **snake_case** (`poi_id`, `full_address`, `poi_type`). The Vue component expects **camelCase** (`poiId`, `fullAddress`, `poiType`) when injecting into the store.

### How to Set Location on a Post (Via UI Interaction ✅ THIS WORKS)

This is the ONLY reliable approach. Do NOT attempt Pinia/Vuex injection or request interception — the publish POST body field names are non-obvious and request interception resulted in location still defaulting to 河北.

```python
async def set_location_on_post(page, keyword):
    \"\"\"Set location on a XHS post via UI interaction.
    
    Args:
        page: Playwright page object (must be on publish page with image uploaded)
        keyword: Location to search for (e.g. 'Covent Garden', '伦敦')
    \"\"\"
    # Step 1: Click "标记地点或标记朋友" to open the location modal
    # NOTE: NOT "添加地点" — that's a different component (内容声明)
    marker = page.get_by_text("标记地点或标记朋友", exact=True)
    await marker.first.click()
    await asyncio.sleep(2)
    
    # Step 2: Switch to "地点" tab (default tab is "用户")
    loc_tab = page.get_by_text("地点", exact=True)
    if await loc_tab.count() > 0:
        await loc_tab.first.click()
        await asyncio.sleep(1)
    
    # Step 3: Find the search input and type keyword
    # The input has placeholder like "搜索用户" or "搜索地点"
    search_inp = page.locator('input[placeholder*="搜索"]')
    if await search_inp.count() > 0:
        await search_inp.first.fill(keyword)
        await asyncio.sleep(3)  # Wait for API response + Vue rendering
        
        # Step 4: Click the first search result
        # The Vue component renders POI results as clickable elements
        # Try poi-bubble class first, fall back to text match
        result = page.locator('.poi-bubble, [class*="poi-item"]').first
        if await result.count() > 0:
            await result.click()
        else:
            # Fallback: click any element containing the first word
            fallback = page.locator(f"text={keyword.split()[0]}").first
            await fallback.click()
        await asyncio.sleep(1)
        
        # Step 5: Click "确定" to confirm and close the modal
        # CRITICAL: Without this, the d-modal-mask overlay blocks 
        # the publish button and you get a TimeoutError
        confirm_btn = page.locator('button:has-text("确定")').first
        if await confirm_btn.count() > 0:
            await confirm_btn.click()
            await asyncio.sleep(1)
            print("  ✓ Location confirmed, modal closed")
```

### Complete Publish Flow with Location

```python
async def post_to_xhs(image_path, title, location_keyword=None):
    \"\"\"Post image to Xiaohongshu with optional location.
    
    Args:
        image_path: Path to the JPEG image file
        title: Post title
        location_keyword: e.g. 'Covent Garden', '伦敦', or None to skip
    \"\"\"
    from playwright.async_api import async_playwright
    import asyncio, json
    
    # Load cookies and fix sameSite
    with open(COOKIE_PATH) as f:
        cookies = json.load(f)
    for c in cookies:
        if c.get("sameSite") not in ("Strict", "Lax", "None"):
            c["sameSite"] = "Lax"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 ...Chrome/120.0"
        )
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        # Step 1: Open publish page
        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&openFilePicker=true",
            wait_until="domcontentloaded", timeout=30000
        )
        await asyncio.sleep(4)
        
        # Step 2: Upload image
        fi = await page.query_selector('input[type="file"]')
        await fi.set_input_files(image_path)
        await asyncio.sleep(8)  # Wait for Vue to render the editor
        
        # Step 3: Set location if requested
        if location_keyword:
            await set_location_on_post(page, location_keyword)
        
        # Step 4: Fill title
        ti = await page.query_selector('input[placeholder*="标题"]')
        if ti:
            await ti.fill(title)
        
        await asyncio.sleep(2)
        
        # Step 5: Publish — use scroll_into_view_if_needed() to ensure
        # button is visible after modal interactions (modal mask blocks otherwise)
        pub = page.locator('button:has-text("发布")').first
        if await pub.count() > 0:
            await pub.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            await pub.click()
            await asyncio.sleep(4)
        
        await browser.close()
```

### 📌 Publish Button — Must Handle Modal Mask

After closing the location modal, a `d-modal-mask` overlay element may still cover the publish button, causing a TimeoutError. **Always use `scroll_into_view_if_needed()` before clicking publish when location was set:**

```python
pub = page.locator('button:has-text("发布")').first
await pub.scroll_into_view_if_needed()
await asyncio.sleep(1)
await pub.click()
```

This ensures the button is truly clickable even if the modal mask partially overlaps it.

### Usage Examples

```python
# Post without location
await post_to_xhs("photo.jpg", "今日穿搭")

# Post with London location
await post_to_xhs("plane_photo.jpg", "飞往伦敦 🛩️", "Covent Garden")

# Post with Shanghai location
await post_to_xhs("coffee.jpg", "上海下午 ☕", "外滩")
```

### Script Reference
Primary (most complete): `/home/admin1/.hermes/profiles/lover/scripts/xhs_post_today.py` — includes SOCKS5 proxy, title rotation (早☀️/今天天气不错/出门/西装日常/周末愉快), cookie sameSite fix, account restriction detection, tab JS click, debug screenshots.
Legacy: `/home/admin1/.hermes/profiles/lover/scripts/xhs_poster_v2.py` — (no proxy, no title rotation)
Legacy: `/home/admin1/.hermes/profiles/lover/scripts/xhs_poster.py` — (basic, no proxy)

### How to Reverse-Engineer API Endpoints (Reusable Technique)

Since xiaohongshu has no public API docs, use JS bundle decompilation:

1. **Navigate to the login page** (no auth needed) — the publish JS bundles load anyway:
   - Login page: `https://creator.xiaohongshu.com/login` (12 bundles loaded)
   - Publish page: `https://creator.xiaohongshu.com/publish/publish` (28 bundles, including publish-specific ones)
2. **Get JS bundle URLs**: `document.querySelectorAll('script[src]')`
3. **Fetch and analyze** the key bundles:
   - `project-publish-vue.*.js` (~1.5MB) — main Vue component with `getSignInfo`, `handleSearch`, `POI search`
   - `project-publish-components.*.js` (~295KB) — sub-components, `PoiSearch`, `poiSearchRef`
4. **Search patterns in JS bundle**:
   - `searchPlace` / `poiSearch` — function names for location search
   - `Foreign` / `Nearby` — enum values in pattern `a[a.X=Y]="Value"`
   - `LV.post` / `LV.get` — axios HTTP calls (search near "poi" / "location" keywords)
   - `GET_POI_LIST` constant → value is the actual API path (constructed via string concat)
   - `getSignInfo` — the Vue method that calls the POI search API
   - `getPositionJurisdiction` — calls `navigator.geolocation.getCurrentPosition()`
5. **API base URLs**:
   - Production: `https://edith.xiaohongshu.com`
   - Path constructed as: `"".concat(baseUrl, "/api/path")`
6. **Environment**: Always unset proxy env vars:
   ```bash
   env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY
   ```
   The WSL env has a broken SOCKS5 proxy (`socks5h://localhost:1080`) that blocks all HTTP.

### Key JS Patterns to Look For

**The Nearby/Foreign enum pattern:**
```javascript
var b = ((a={})[a.Nearby=1]="Nearby", a[a.Home=2]="Home", a[a.Foreign=3]="Foreign", a);
```

**The getSignInfo function (Vue method that calls the API):**
```javascript
async getSignInfo() {
    this.longitude || this.latitude || await this.getPositionJurisdiction();
    // For location type:
    let e = {keyword: this.keyword, page: this.page, size: this.pageSize,
             longitude: this.longitude, latitude: this.latitude,
             source: "WEB", searchContext: this.searchContext || void 0,
             type: this.keyword ? es.jK.Foreign : es.jK.Nearby};
    let t = await (0, es.RC)(e);  // ← RC = C function = LV.post(GET_POI_LIST, e)
}
```

**Actual publish request structure (from network interception — WITHOUT location):**
```json
{
  "common": {"type": "normal", "title": "...", "desc": "", "hash_tag": [], ...},
  "image_info": {"images": [{"file_id": "...", "width": 3584, "height": 4800, "stickers": {"floating": []}}]},
  "video_info": null
}
```

**With location set via UI (the sticker appears in `image_info.images[0].stickers.floating`):**
```json
{
  "image_info": {
    "images": [{
      "stickers": {
        "floating": [{
          "style": 1,
          "type": "location",
          "event": {"value": {"id": "B0KBXCHXEB", "name": "Covent Garden"}},
          "container_size": "{300, 224}",
          "unit_center": null,
          "anchor_center": "{0.82..., 0.5}",
          "mark_y": 0.5
        }]
      }
    }]
  }
}
```

**⚠️ CRITICAL: Location is NOT a top-level field.** It's embedded as a sticker on the image. The sticker `id` (e.g., `B0KBXCHXEB`) is **different** from the POI search API's `poi_id` (e.g., `P0J169J4HL`). The Vue component generates a new sticker ID when the user clicks a search result — you cannot derive it from the POI API response alone. This is why request interception injection does NOT reliably set post locations.

**The only reliable approach is the UI interaction method above.**

### Other API Endpoints Found in JS Bundles

| Endpoint | Purpose |
|----------|---------|
| `POST /web_api/sns/v2/note` | Publish/update note |
| `POST /web_api/sns/v1/local/poi/creator/search` | **POI/location search** (verified working) |
| `POST /web_api/sns/v5/creator/poi/search` | Legacy POI search (different endpoint) |
| `POST /api/sns/capa/servicegw/web/getpoilist` | Alternative POI API |
| `GET /api/galaxy/user/my-info` | User info |
| `POST /web_api/sns/v1/search/label` | Sign category info |
| `POST /web_api/sns/v5/creator/file/encryption` | Get signed upload URL |

### Cookie Management
- Store cookie file locally: `~/.hermes/profiles/lover/xhs_cookies.json`
- Mirror on Windows: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/xhs_cookies.json`
- **Fix sameSite**: Chrome exports `unspecified` — must change to `Lax`
- Cookie expiry: ~30 days (check `expirationDate` field), but **access-token-creator.xiaohongshu.com** may last 6+ months. **⚠️ Even access tokens can silently expire** — the only reliable test is navigating to the publish page and checking for redirects.
- **⚠️ Cookie expiry manifests as captcha redirect, NOT toast/error** — if you see `xiaohongshu.com/web-login/captcha?redirectPath=...&verifyType=124&verifyBiz=461` in the page URL, it means cookies are invalid and need re-export

### Cookie Pre-Validation (Before Launching Playwright)

Before starting a Playwright session (especially in cron jobs), pre-check cookie expiration dates to avoid spending 30-60s on a failed attempt:

```python
import json, time

with open(COOKIE_PATH) as f:
    cookies = json.load(f)
now = time.time()
cookies_valid = True
for c in cookies:
    exp = c.get('expirationDate', 0)
    remaining = exp - now if exp else None
    name = c.get('name', '?')
    if remaining and remaining < 0:
        print(f'⚠️ Cookie "{name}" expired {abs(remaining)/86400:.1f}d ago')
        cookies_valid = False
    elif remaining:
        print(f'  Cookie "{name}" valid for {remaining/86400:.1f}d')

if not cookies_valid:
    print("❌ Cookies expired — need fresh export. Skipping Playwright.")
    return  # or exit
```

**Critical cookies that must all be valid:**
- `acw_tc` — anti-crawler token (lifespan ~7 days). **If expired → captcha redirect regardless of other cookies.**
- `websectiga` — security token (~3-7 days)
- `access-token-creator.xiaohongshu.com` — main auth (~6 months), but useless without `acw_tc`
- `customer-sso-sid` — SSO session (~30 days)

Even with a valid long-lived access token, an expired `acw_tc` will redirect to captcha. This is the most common failure mode after ~7 days.

### Cookie Expiry Timeline (Observed)

Expected cookie lifespan from a single export:
| Cookie | Lifespan | Failure Mode |
|--------|----------|-------------|
| `acw_tc` | ~7 days | Captcha redirect at publish page |
| `websectiga` | ~3-7 days | Captcha redirect |
| `sec_poison_id` | ~7 days | Session errors |
| `access-token-creator` | ~6 months | Still valid but blocked by captcha |
| `customer-sso-sid` | ~30 days | SSO session expired |

**Real-world observation (May 5, 2026):** Cookies exported Apr 28 expired after ~7 days. The `acw_tc` anti-crawler cookie expires first, blocking all requests even though the access token is still valid for months. After ~7 days without a fresh export, Playwright always redirects to captcha.
- For multiple accounts: store as `cookies_account1.json`, `cookies_account2.json`
- One-time export from user via EditThisCookie Chrome extension
- **Persistence across sessions**: Cookies at the profile-level path (`~/.hermes/profiles/lover/xhs_cookies.json`) survive between conversation sessions and Python venv resets. This is critical because the script files in /tmp/ and working directories are frequently lost.
- **⚠️ Python environment dependency**: Run Playwright scripts with the **system python3.10** (`/usr/bin/python3.10`) not the hermes-agent venv python3.11, because playwright + PySocks are only installed in the system Python.

### Post Frequency Limit
XHS may rate-limit aggressive auto-posting. Recommend 1 post/day max.

## Cron Job Setup for Daily Auto-Post

```python
# See cronjob tool for scheduling
# Script to use: ~/.hermes/profiles/lover/scripts/xhs_post_today.py
# This is the ONLY script with proxy support, title rotation, and restriction detection.
# Schedule: daily at 9:00 AM
```

### Cron Job Parameters
```json
{
  "action": "create",
  "name": "xhs-daily-post",
  "schedule": "0 9 * * *",
  "prompt": "Run xhs_post_today.py: env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY /usr/bin/python3.10 /home/admin1/.hermes/profiles/lover/scripts/xhs_post_today.py",
  "skills": ["xiaohongshu-auto-publish", "gemini-image-generation", "intimate-roleplay-technical-implementation"],
  "enabled_toolsets": ["terminal", "file"]
}
```

## Verification Checklist
After each auto-post:
- [ ] Image was generated (check output directory for new file)
- [ ] Playwright navigated to publish page
- [ ] Image uploaded successfully (wait 6s for form)
- [ ] Title entered correctly
- [ ] Publish button clicked
- [ ] "发布成功" confirmed in page text
- [ ] User notified via Feishu

## Common Failures & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `NoneType has no attribute set_input_files` | File input not in DOM | Navigate to URL with `openFilePicker=true` parameter, or click "上传图文" tab first |
| Playwright timeout on navigation | `networkidle` never fires | Use `domcontentloaded` instead |
| `sameSite` error adding cookies | Cookie has `"unspecified"` value | Change to `"Lax"` |
| Page shows initial upload screen instead of form | File input not triggered | Use `fi.set_input_files()` directly (don't click button) |
| Image uploads but form doesn't render | Not enough wait time | Increase sleep to 5-6s after upload |
| `Locator.click: Element is outside of the viewport` on "上传图文" | Nested span in scrollable container | **Use JS click** — `page.evaluate()` with `el.click()` on parent div/button |
| `ModuleNotFoundError: No module named 'playwright'` | Wrong Python venv | Use `/usr/bin/python3.10` (system), not hermes-agent venv |
| `Missing dependencies for SOCKS support` | Hermes-venv pip broken | Install playwright via system pip: `pip3 install playwright` (user site-packages) |
| Toast: "因违反社区规范禁止发笔记" | Account restricted from auto-testing | User must check XHS notifications and appeal; delete cookies from config |
| Through-proxy HTTPS failures to IP checkers | Domestic VPN routing | Use response time to XHS (~0.2s) as proxy health signal instead |
| File upload "succeeds" but page stays on tab selector | Upload triggered before tab switch | Must click "上传图文" tab BEFORE upload via **JS click** (Playwright .click() fails) |
| Publish click succeeds but URL stays on `/publish?from=tab_switch` | Publish request may fail silently or need JS dispatchEvent fallback | Check for toast messages via `page.evaluate()`; try JS dispatchEvent fallback |
### 🚨 Account Restriction Detection (Critical Safety Check)

After uploading an image and attempting to publish, always check TWO things: standard toast elements AND post-publish page state (banned accounts may silently fail without visible toasts).

```python
async def check_publish_restriction(page):
    """Check if the account is restricted from publishing."""
    toasts = await page.evaluate("""() => {
        const alerts = [];
        const toasts = document.querySelectorAll('[class*="toast"], [role="alert"]');
        for (const t of toasts) alerts.push(t.textContent);
        return alerts;
    }""")
    for t in toasts:
        if any(w in t for w in ["禁止", "违规", "限制"]):
            return t
    return None
```

**Known restriction message:** `"因违反社区规范禁止发笔记"` — this is a publish ban, not a login ban. Account can still log in and browse but cannot publish.

**When detected:**
1. Print `🚫 ACCOUNT RESTRICTED: {toast_text}`
2. Inform user to check XHS notifications and appeal
3. **Delete cookies** — the auth is useless if publishing is banned
4. Clean config.json — remove XHS account fields (keep Gemini key + face template)
5. User needs new account to restart

### 📸 Screenshot Debugging Strategy

When Playwright scripts fail, always save screenshots to Windows desktop for user to view:
```python
await page.screenshot(path="/tmp/xhs_debug_screenshot.png")
import shutil
shutil.copy("/tmp/xhs_debug_screenshot.png", 
    "/mnt/c/Users/Administrator/Desktop/xhs_debug.png")
print("📸 Screenshot on desktop: xhs_debug.png")
```

Common failure patterns visible on screenshots:
- **Blank page / login page** → Cookie expired
- **Tab selector visible (上传视频/上传图文/写长文)** → Tab not clicked before upload
- **Form with image uploaded** → Upload success, check next step
- **Form with "禁止发笔记" toast** → Account restricted
| SOCKS5 proxy "connection refused" on 172.20.128.1:10808 | v2rayN not running or LAN access not enabled | Ask user to: (1) start v2rayN, (2) enable "允许来自局域网的连接", (3) check Windows Firewall |
| `Locator.click: Element is outside of the viewport` on any publish page element | Scrollable nested containers | Use `page.evaluate()` with JS `dispatchEvent()` or `el.click()` on parent container |
| `os.path.expanduser("~")` resolves to wrong path | Hermes-agent overrides HOME env var to profile directory | Use absolute paths in all scripts (e.g. `/home/admin1/.hermes/profiles/lover/config.json`, never `~/.hermes/...`) |
| QR code/captcha page shown instead of publish form | Too many automated Playwright sessions in short period — XHS flags the activity | Limit to 1-2 Playwright sessions per run; space out consecutive runs by at least 10 minutes |
| Cookies redirect to `xiaohongshu.com/web-login/captcha` | Cookies expired or session invalid | User must re-export cookies from Chrome via EditThisCookie; old cookies (even with valid-looking access tokens) silently expire after ~7-30 days |
| Publish click yields no error but page stays on editor form | Banned account — API silently rejects publish request | Check for silent failure via `check_account_restriction(page, after_publish=True)`; need new account |

## Related Skills
- `gemini-image-generation` — API details for Gemini img2img
- `intimate-roleplay-technical-implementation` — face template discovery workflow, 痞帅体育生 aesthetic
- `wsl-sd-feishu-pipeline` — Feishu delivery integration

## References
- `references/playwright-publish-guide.md` — Playwright-based auto-publishing: cookie setup, face template strategy, Playwright interaction patterns, account ban detection, full pipeline scripts (v1/v2), daily title rotation, POI/location reverse engineering
- `references/semi-automated-daily-pipeline.md` — Semi-automated alternative: Gemini img2img → Feishu delivery → user manually posts (zero ban risk), 7-day thematic schedule, caption templates, PowerShell generation scripts
