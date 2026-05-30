---
name: toapis-image-generation
description: Generate images via toapis.com API gateway — OpenAI-compatible gateway supporting GPT-Image-2 (image2.0) and Gemini image models. Async task-based generation with image upload workflow. SOCKS5 proxy required for API calls.
version: 1.1.0
author: Lover
metadata:
  hermes:
    tags: [toapis, image-generation, api-gateway, gpt-image-2, async]
    related_skills: [gemini-image-generation]
---

# ToAPIs Image Generation (API Gateway)

## Overview

[toapis.com](https://docs.toapis.com/docs/cn) is an OpenAI-compatible API gateway supporting GPT-5, Claude, Gemini, and image/video models. The image generation API uses an **async task workflow**: submit a generation request, poll for completion, download the result.

### ⚠️ CRITICAL WARNING: "gpt-image-2" is NOT real OpenAI GPT-Image-2 (Discovered 2026-05-12)

**This is the single most important pitfall in this skill.** The model marketed as "gpt-image-2" on toapis.com does NOT produce output equivalent to the real OpenAI GPT-4o Image 2.

| Aspect | Real OpenAI GPT-4o Image 2 (chatgpt.com) | toapis "gpt-image-2" |
|--------|-----------------------------------------|---------------------|
| Body proportions | ✅ Normal, natural proportions | ❌ Distorted — short legs, big/small head, weird limbs |
| Skin/hair detail | ✅ Detailed, realistic | ❌ Often "smooth/plastic" look |
| Leg hair | ✅ Can render natural leg hair | ⚠️ Inconsistent — may skip fine details |
| Feet in frame | ✅ Fits two feet naturally | ❌ Often crops or distorts feet |
| Reliability | ✅ Consistent quality | ⚠️ Variable, unreliable for body-specific prompts |

**Evidence (2026-05-12):**
1. Generated two versions (with/without leg hair) using same prompt → both had wrong body proportions
2. User tested same prompt on chatgpt.com (real GPT-4o Image 2) → "身体比例就是正常的"
3. The model name "gpt-image-2" does NOT match any official OpenAI model name (OpenAI uses `gpt-4o` chat completion with image params, or `dall-e-3`)

**Conclusion:** toapis "gpt-image-2" is likely a repackaged open-source model (SD variant or fine-tune) with poor body proportion handling. For reliable image generation, use **chatgpt.com (real GPT-4o Image 2)** with prompts written by Lover, OR find a trustworthy third-party API that actually proxies the real OpenAI model.

**Workaround when stuck using toapis:**
- Keep prompts **scene-focused only** (no body-type adjectives, no detailed anatomy descriptions)
- Use reference images to carry body proportions
- Accept that results will be mediocre — consider this a last resort when OpenAI is inaccessible

### Key Differences from Gemini Direct API

| Aspect | Gemini Direct | toapis (any model) |
|--------|--------------|-------------------|
| Response | Synchronous (direct URL in response) | Async (task ID → poll) |
| Image upload | Base64 in prompt | Upload first → use URL |
| Safety filters | Strict (blocks NSFW/editorial) | More lenient (commercial fashion OK) |
| Cost | Free tier limited | ~0.105元/1K image, ~0.42元/2K |
| Proxy | SOCKS5 required | SOCKS5 required |
| **Body proportion accuracy** | ✅ Good | ❌ **Poor — use only as fallback** |

### ⚠️ PITFALL: API key not in config (first-time setup)

The toapis API key may be stored under **two different names** depending on when it was set up:

**Check config.json (`cat ~/.hermes/profiles/lover/config.json`) for either:**
```json
{
  "toapis_api_key": "sk-...SAyO",        // preferred name — may be blank/provided by user
  "image20_api_key": "sk-...SAyO",       // actual stored name from older setup ✅
  "image20_endpoint": "https://toapis.com/v1",
  "image20_model": "gpt-4o-image"        // IGNORE this model — use gpt-image-2 instead
}
```

The config.json uses **`image20_api_key`** as the key name, not `toapis_api_key`. If you only search for `toapis_api_key`, you'll miss it and think the key is missing.

**If still not found, check 重要记事.md:**
```bash
cat ~/.hermes/profiles/lover/notes/重要记事.md
```
The user may have noted the key there. If absent from both, tell the user.

**Still stuck?** Google (generativelanguage.googleapis.com, aistudio.google.com) is **completely unreachable** from this WSL environment (exit code 7, failed to connect). The toapis gateway via SOCKS5 proxy is the **only viable image generation path** — no Gemini fallback, no key to generate.

### ⚠️ PITFALL: DOUBLE /v1/ IN URL (Wasted ~3 minutes debugging this)

The skill templates use `BASE = "https://toapis.com"` and all API paths include `/v1/` explicitly:
```python
BASE = "https://toapis.com"
resp = requests.post(f"{BASE}/v1/uploads/images", ...)  # → https://toapis.com/v1/uploads/images ✅
```

**BUT** the config.json stores `toapis_base_url: "https://toapis.com/v1"`. If you use that as BASE and then also prepend `/v1/` to paths:
```python
BASE = "https://toapis.com/v1"          # from config.json
resp = requests.post(f"{BASE}/v1/uploads/images", ...)  # → https://toapis.com/v1/v1/uploads/images ❌
```

**Fix**: Always hardcode `BASE = "https://toapis.com"` (no `/v1` suffix) and let the path templates append `/v1/...`. Ignore the `toapis_base_url` from config.json for the base constant — it's only useful as documentation of the service root.

---

## Supported Image Models

| Model | Description | Best For |
|-------|------------|----------|
| `gpt-image-2` | OpenAI GPT-Image-2 ("image2.0") | text2img + reference_images img2img |
| `gpt-4o-image` | GPT-4o image | text2img, simpler API |
| `gemini-3.1-flash-image-preview` | Google Gemini (via gateway) | Same as direct Gemini |
| `gemini-3-pro-image-preview` | Google Gemini 3 Pro | Higher quality |
| `seedream-4.5` | Seedream 4.5 | Anime/illustration style |

**Default choice**: `gpt-image-2` — best for realistic product photos with reference guidance.

### ⚠️ PITFALL: gpt-4o-image pricing failure

`gpt-4o-image` returns HTTP 500 with `pricing_failed: "no matching pricing rule for family gpt-4o-image"`. This model is **not usable** on toapis.com with the current account. Always use `gpt-image-2` for image generation.

### ⚠️ PITFALL: Large PNG uploads timeout through SOCKS5 proxy

Skin 02 reference PNGs (5-10MB) will **time out** when uploading through the SOCKS5 proxy (120s read timeout).

**Fix**: Compress PNG to JPEG first, max 2048px on longest side, quality=90:
```bash
python3 -c "
from PIL import Image
img = Image.open('large.png').convert('RGB')
w, h = img.size
if max(w, h) > 2048:
    ratio = 2048 / max(w, h)
    img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)
img.save('compressed.jpg', 'JPEG', quality=90)
"
```
Result: 10.3MB → 276KB, upload succeeds.

### ⚠️ PITFALL: Task stuck at 'queued' for minutes

Generation tasks sometimes stay `queued` for 3+ minutes before moving to `in_progress`. **Do NOT time out early** — poll for at least 300s. If the first poll loop times out, re-query the same task_id — it may have completed while you weren't polling.

### ⚠️ PITFALL: Feishu MEDIA: attachment doesn't work

`send_message()` with `MEDIA:/path/to/file` **silently omits the attachment for Feishu**. Images must be delivered via Feishu API:
1. Get tenant access token (app_id + app_secret)
2. Upload image to `https://open.feishu.cn/open-apis/im/v1/images`
3. Send as `msg_type: "image"` with the returned `image_key`
- See `references/user-ref-pic-system.md` for full Feishu delivery code.

Even though the API accepts `response_format: "url"`, the downloaded image files are **actually PNG format** (magic bytes `‰PNG`) regardless of file extension. When saving, either:
- Save as `.png` extension, or
- Re-encode to JPEG with Pillow: `Image.open(path).convert('RGB').save(path, 'JPEG', quality=92)`

Feishu upload accepts PNG, but for consistency with Gemini images (which return true JPEG), convert to JPEG via Pillow before delivery.

---

## API Configuration

### Credentials

**Do NOT assume the key is stored under `toapis_api_key`.** The actual config.json (`~/.hermes/profiles/lover/config.json`) stores it as `image20_api_key`:

```json
{
  "gemini_api_key": "AIzaSy...t_u8",
  "gemini_model": "gemini-3.1-flash-image-preview",
  "image20_api_key": "sk-nI0...SAyO",      // ← THIS is the actual toapis key
  "image20_provider": "toapis.com",
  "image20_endpoint": "https://toapis.com/v1",
  "image20_model": "gpt-4o-image",          // ← DO NOT USE: gpt-4o-image returns pricing_failed 500
  "ref_face_path": "/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg"
}
```

Also check 重要记事.md (`cat ~/.hermes/profiles/lover/notes/重要记事.md`) if not found in config.json.

**Always use model `gpt-image-2`** — `gpt-4o-image` (what `image20_model` says) fails with `pricing_failed: "no matching pricing rule"`.

### Network

**toapis API calls MUST use SOCKS5 proxy** (V2Ray overseas node):
```python
socks_proxies = {"http": "socks5://172.20.128.1:10808", "https": "socks5://172.20.128.1:10808"}
requests.post(url, proxies=socks_proxies, ...)
```

**Feishu uploads must BYPASS proxy:**
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
```

---

## Image Generation Workflow

### Step 1: Upload Reference Images

```python
import requests

API_KEY = "sk-..."
BASE = "https://toapis.com"
PROXY = "socks5://172.20.128.1:10808"
proxies = {"http": PROXY, "https": PROXY}

def upload_image(path):
    with open(path, "rb") as f:
        resp = requests.post(f"{BASE}/v1/uploads/images",
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": f},
            proxies=proxies)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Upload failed: {data}")
    return data["data"]["url"]
```

**Limits:**
- Max file size: 10MB
- Supported formats: JPEG, PNG, WebP, GIF
- Uploaded URL can be reused across multiple generations
- No base64 in generation requests — must upload first

### Step 2: Submit Generation Task

```python
payload = {
    "model": "gpt-image-2",
    "prompt": "...",
    "n": 1,
    "size": "2:3",    # Aspect ratio
    "resolution": "1K",  # 1K | 2K | 4K
    "response_format": "url",
    "reference_images": [url1, url2, url3]  # img2img references
}

resp = requests.post(f"{BASE}/v1/images/generations",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json=payload,
    proxies=proxies)

task = resp.json()
task_id = task.get("id") or task.get("task_id")
```

### Step 3: Poll for Result

```python
import time

def wait_for_result(task_id, max_wait=180):
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{BASE}/v1/images/generations/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            proxies=proxies)
        result = resp.json()
        status = result.get("status")
        
        if status == "completed":
            r = result.get("result", {})
            items = r.get("data", [])
            if items and items[0].get("url"):
                return items[0]["url"]  # Download this URL
        elif status == "failed":
            raise RuntimeError(result.get("error", {}).get("message"))
        
        time.sleep(3)
    
    raise TimeoutError("Task timed out")
```

Typical generation time: **30-60 seconds** for 1K, **60-120 seconds** for 2K.

### Step 4: Download and Save

```python
img_resp = requests.get(img_url, proxies=proxies, timeout=30)
with open("output.jpg", "wb") as f:
    f.write(img_resp.content)
```

**⚠️ Images expire after 24 hours.** Download immediately.

---

## Size & Resolution Table

### 1K (~0.105元/image, ~37s actual)

| Size | Resolution | Supported? |
|------|-----------|------------|
| `1:1` | 1024×1024 | ✅ |
| `3:2` | 1536×1024 | ✅ |
| `2:3` | 1024×1536 | ✅ (portrait, closest to 9:16) |

### 2K (~0.42元/image est., ~15s actual)

| Size | Resolution | Supported? |
|------|-----------|------------|
| `1:1` | 2048×2048 | ✅ |
| `9:16` | **1152×2048** | ✅ **(phone aspect, confirmed)** |
| `4:3` | 2048×1536 | ✅ |
| `3:4` | 1536×2048 | ✅ |

### 4K (~13s actual)

| Size | Resolution | Supported? |
|------|-----------|------------|
| `16:9` | 3840×2160 | ✅ |
| `9:16` | 2160×3840 | ✅ (confirmed) |
| `21:9` | 3840×1648 | ✅ |

**Note**: Actual generation times observed in practice are significantly faster than the skill's estimates — 1K ~37s, 2K ~15s, 4K ~13s. However, the variation may be due to server load. Timeouts in the polling loop should still use 180s max.

**Also note**: `9:16` aspect ratio only works as a `size` parameter value for 2K and 4K. For 1K, use `size: "2:3"` (1024×1536) which is the closest portrait aspect to 9:16.

**Recommendation:** For product photos → use **1K 2:3** (cheapest, good enough for Feishu/闲鱼). Use **2K 9:16** only when user explicitly requests higher quality.

---

## Prompt Engineering for gpt-image-2

### GOLDEN RULE: gpt-image-2 is NOT Gemini

**They need fundamentally different prompting approaches.** Using Gemini-style prompts on gpt-image-2 produces bad results.

| Aspect | Gemini (Direct) | gpt-image-2 (ToAPIS) |
|--------|----------------|---------------------|
| Body descriptions | Can handle moderate body adjectives in prompt | Stacking body adjectives causes balloon/extreme body parts |
| Reference images | img2img as base64 inline | Multiple uploaded images + clean prompt works best |
| Negative framing | `not lean, not defined` works okay | Multiple negations confuse the model (overcorrects) |
| Scene description | Needs to carry more weight | Let references do body work; prompt = just scene |

### CRITICAL: User's explicit directive (May 5, 2026)

After getting thighs that looked "like balloons" from stacked body adjectives, user said:

> **"直接描述场景衣服表情动作情景啥的就好了"**
> "Just describe the scene, clothes, expression, action, setting — that's enough."

**This is a hard rule for gpt-image-2:** When using good reference images (face + full-body), the prompt should contain ZERO body-type adjectives. Just describe what happens in the scene.

### Correct Approach for gpt-image-2

```
# WRONG (Gemini-style — stacked body adjectives):
"sitting at table, extremely thick massive tree trunk thighs, fat-covered muscle, 
rugby player build, not lean not defined..."

# CORRECT (gpt-image-2 — clean scene, references handle body):
"A candid realistic photo of a young man aged 18-22 with warm fair mixed-race skin, 
sitting barefoot at a wooden dining table at night eating dinner with chopsticks. 
Wearing a plain white t-shirt and soft grey shorts. One foot rests on the floor, 
the other hooked around a chair leg. Warm evening indoor lighting, cozy home atmosphere."
```

### Reference Strategy for gpt-image-2

**Dual reference (face + full-body) is the secret to good gpt-image-2 results:**

```python
ref_urls = [
    upload("37_portrait_front.jpg"),     # Face reference (1号皮肤)
    upload("gemini_fullbody_ref.jpg"),   # Full-body reference (generated by Gemini)
]
payload["reference_images"] = ref_urls
# Prompt = just scene description, no body adjectives
```

- Face reference (37_portrait_front.jpg / 1号皮肤) provides facial consistency
- Full-body reference provides body proportions, leg thickness, and overall frame
- The model will naturally blend both — let the references work, don't fight them
- **If body parts are wrong (too thin / too fat):** Fix the reference images, NOT the prompt
- For generating the full-body reference itself, use **Gemini** (it handles body + face together better)
- The full-body reference image lives at: `audio_cache/gemini_fullbody_ref.jpg` (generated 2026-05-05 with Gemini, 37 face + shirtless swim trunks prompt)

### Structure
```
[Scene/setting] + [subject action] + [clothing details] + [lighting/mood]
```
No body-type adjectives when good references are provided.

### Key Patterns

- Use: `candid realistic photo`, `realistic snapshot`, `natural everyday moment`
- Avoid: `editorial`, `commercial photography`, `fashion` (gives posed look for this user)
- Avoid ALL: `sexy`, `seductive`, `intimate`, `muscular` (triggers safety filters)
- **CRITICAL: The thickness pendulum problem.** Extreme language like `EXTREMELY THICK`, `FAT-COVERED MUSCLE`, `massive like tree trunks` stacked together pushes GPT-Image-2 from "lean" to "obese" with no middle ground. If you must describe body, use body-type analogies:
  - ✅ `rugby player build`, `heavyweight athlete`, `powerlifter legs`, `big solid frame`
  - ✅ `visible natural fullness over strong underlying mass`, `not skinny, not obese`
  - ❌ `FAT-COVERED MUSCLE` + `tree trunk thighs` + `massive circumference` stacked (→ obese)
  - ❌ `Thick heavy round massive` alone without analogy (→ still slim, AI defaults thin)
  - **Best approach**: ONE key analogy + "not X, not Y" framing = most reliable, BUT even better = skip body entirely and let reference images work
- **Skin tone**: NEVER use `cold pale white skin` or `pale white` — this user has **mixed-race (Eurasian) fair skin with warm undertones**. Write: `fair mixed-race skin with warm ivory undertones`, `Eurasian fair skin tone`, `mixed heritage warm complexion`
- Keep prompts shorter than 4000 chars (GPT-Image-2 limit)
- See `references/body-description-prompting.md` for full iteration log
- For socks: be anatomically precise — `sock hem sits 2-3cm above the ankle bone`, `exposing entire ankle and lower calf`
- For shoes: `slightly worn`, `natural creasing`, `gentle wear marks` (not pristine new)

### Example (Tesla Model Y driver's seat):
```
"A lifestyle commercial photography shot inside a Tesla Model Y, 
first-person driver's seat point of view looking down at the driver's legs. 
The white socks are SHORT mid-calf socks — the white sock cuff sits ONLY 
2-3 CENTIMETERS above the ankle bone... On his feet are slightly worn white 
Nike Air Force 1 sneakers with natural creasing... Thick heavy round massive 
legs with cold pale white skin... Natural car interior lighting with soft 
window light."
```

---

## Common Errors & Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `401 unauthorized` | Bad API key | Check `Authorization: Bearer` header |
| `402 insufficient_quota` | Out of balance | Top up account |
| `422 content_policy_violation` | NSFW trigger | Rewrite prompt as commercial/editorial |
| `429 rate_limit_exceeded` | Too fast | Add 3s delay between requests |
| Task stuck at `in_progress 10%` | Model busy | Wait up to 180s max |
| `Connection refused` (Feishu) | Proxy interference | Unset proxy env vars |

### Proxy Gotchas
- The Python `requests` library picks up `http_proxy` env vars from Hermes automatically
- **toapis.com** needs SOCKS5 → use `--socks5-hostname 172.20.128.1:10808` with curl or `proxies=dict` with requests
- **Feishu API** must bypass proxy → use `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` before running
- **Git** also needs `unset http_proxy` before pushing to GitHub

---

## Cost Comparison (per image, 1K)

| Provider | Model | Price | Speed |
|----------|-------|-------|-------|
| toapis.com | gpt-image-2 1K | ~0.105元 | ~56s |
| toapis.com | gpt-image-2 2K | ~0.42元 (est) | ~90s |
| Gemini API | gemini-3.1-flash | Free tier limited | ~35s |
| Gemini API | gemini-2.5-flash | Free tier limited | ~25s |

---

## Full Python Workflow Script

Save as a template in `templates/toapis_generation.py`:

```python
#!/usr/bin/env python3
"""Generate image via toapis.com GPT-Image-2"""

import requests, time, json, os, sys

API_KEY = os.environ.get("TOAPIS_API_KEY", "sk-...")
BASE = "https://toapis.com"
PROXY = "socks5://172.20.128.1:10808"
proxies = {"http": PROXY, "https": PROXY}

def upload_image(path):
    with open(path, "rb") as f:
        resp = requests.post(f"{BASE}/v1/uploads/images",
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": f},
            proxies=proxies)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Upload failed: {data}")
    return data["data"]["url"]

def generate(prompt, ref_urls=[], size="2:3", resolution="1K"):
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "resolution": resolution,
        "response_format": "url"
    }
    if ref_urls:
        payload["reference_images"] = ref_urls
    
    resp = requests.post(f"{BASE}/v1/images/generations",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload, proxies=proxies)
    return resp.json().get("id")

def poll(task_id, max_wait=180):
    start = time.time()
    while time.time() - start < max_wait:
        resp = requests.get(f"{BASE}/v1/images/generations/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}, proxies=proxies)
        result = resp.json()
        status = result.get("status")
        if status == "completed":
            return result["result"]["data"][0]["url"]
        elif status == "failed":
            raise RuntimeError(str(result.get("error")))
        time.sleep(3)
    raise TimeoutError()

# Usage
if __name__ == "__main__":
    ref = upload_image("reference.jpg")
    task_id = generate("your prompt here", [ref])
    img_url = poll(task_id)
    print(f"Result: {img_url}")
```

---

## References

- [Official Docs](https://docs.toapis.com/docs/cn)
- [llms.txt — full index](https://docs.toapis.com/llms.txt)
- [Upload API](https://docs.toapis.com/docs/cn/api-reference/uploads/images)
- [Image Generation API](https://docs.toapis.com/docs/cn/api-reference/images/gpt-image-2/generation)
- [Task Status API](https://docs.toapis.com/docs/cn/api-reference/tasks/image-status)
- `references/body-description-prompting.md` — Body thickness pendulum problem iteration log
- `references/user-ref-pic-system.md` — User's reference image directory (ref_pic/, organized by skin01/skin02). **Check this file first** when choosing a reference image for a generation task. Each file has descriptions of pose, clothing, and best use case.
