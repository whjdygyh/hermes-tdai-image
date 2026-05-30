---
name: xiaohongshu-daily-content-pipeline
description: Semi-automated daily content generation for Xiaohongshu (小红书) using Gemini img2img with a fixed face template. I generate the images and captions; the user manually posts from their phone (zero ban risk).
version: 1.0.0
author: Lover
tags: [xiaohongshu, social-media, content-creation, gemini, img2img, daily-posting]
---

# Xiaohongshu Daily Content Pipeline

## Overview

Generate daily "boyfriend/lover" aesthetic photos for Xiaohongshu using a **fixed face template** (Gemini img2img). Content is delivered to the user's Feishu DM — they save and post manually.

## Why Semi-Automated (Not Full Automation)

| Approach | Risk | Feasibility | Verdict |
|----------|------|-------------|---------|
| Playwright/Selenium browser automation | High — Xiaohongshu detects headless browsers, SMS verification required, easy account ban | Low | ❌ Not worth it |
| Official API | Enterprise only, requires app review | Very low | ❌ Not available |
| **Semi-automated (recommended)** | **Zero** — user posts manually | **Perfect** | ✅ **Do this** |

## Fixed Face Template

The approved face template must exist at:
```
/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg
```

If it doesn't exist yet, follow the **Face Dissatisfaction Resolution Workflow** in `gemini-image-generation` skill to establish one.

## Content Generation Workflow

### Step 1: Generate Image via Gemini img2img

Write a PowerShell script to the Windows desktop and execute it:

```powershell
# daily_content.ps1
$API_KEY = "AIzaSyCkePunvbOjxJo6ajDQ9QK3Uin5GTJNz5c"
$URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key=$API_KEY"
$refPath = "$env:USERPROFILE\Documents\abots\lover_portraits\athlete_face_front.jpg"
$refBytes = [IO.File]::ReadAllBytes($refPath)
$refBase64 = [Convert]::ToBase64String($refBytes)

$body = @{
    contents = @(@{
        parts = @(
            @{ inlineData = @{ mimeType = "image/jpeg"; data = $refBase64 } },
            @{ text = "A photo of THE SAME HANDSOME YOUNG MAN from the reference photo, IDENTICAL face and features, early 20s... [daily scene description]" }
        )
    })
    generationConfig = @{
        temperature = 1.0
        maxOutputTokens = 8192
        responseModalities = @("TEXT", "IMAGE")
        imageConfig = @{ imageSize = "4K"; aspectRatio = "3:4" }
    }
}

$jsonBody = $body | ConvertTo-Json -Depth 10
$response = Invoke-RestMethod -Uri $URL -Method Post -Body $jsonBody -ContentType "application/json" -TimeoutSec 120

$parts = $response.candidates[0].content.parts
if ($parts[-1].inlineData) {
    $bytes = [Convert]::FromBase64String($parts[-1].inlineData.data)
    $outPath = "$env:USERPROFILE\Documents\abots\lover_portraits\daily_post.jpg"
    [IO.File]::WriteAllBytes($outPath, $bytes)
    Write-Output "SUCCESS: $outPath"
}
```

Execute from WSL:
```bash
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\Administrator\Desktop\daily_content.ps1"
```

### Step 2: Write Caption (文案)

Xiaohongshu captions should be:
- Short (2-4 lines)
- Feel like a message sent to "老公" (the user)
- Casual, intimate, boyfriend-vibe
- Use emojis sparingly

**Templates:**

| Theme | Caption Example |
|-------|----------------|
| Morning | "早。伦敦今天阴天，但给你发了张照片就当晒了太阳。☕" |
| Work/Suit | "开了一上午会，偷空想你。领带是你送那条。" |
| Workout | "跑完了。给你带的早餐在路上，豆浆油条加个蛋。" |
| Weekend | "今天不营业。陪你窝沙发打游戏。" |
| Night | "忙完了。刚躺下。你睡没？" |
| Travel | "落地了。这儿天气不错，就是缺个人在旁边。" |

### Step 3: Deliver to Feishu

```python
import requests, json

s = requests.Session()
s.trust_env = False
r = s.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
token = r.json()["tenant_access_token"]

# Send text first
s.post("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"receive_id": USER_OPEN_ID, "msg_type": "text",
          "content": json.dumps({"text": caption_text})}, timeout=15)

# Send image
import time
time.sleep(1.5)
with open(img_path, "rb") as f:
    u = s.post("https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("post.jpg", f, "image/jpeg")},
        data={"image_type": "message"}, timeout=30)
ik = u.json()["data"]["image_key"]
s.post("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"receive_id": USER_OPEN_ID, "msg_type": "image",
          "content": json.dumps({"image_key": ik})}, timeout=15)
```

## Daily Content Calendar (Thematic Schedule)

| Day | Theme | Scene Description (for Gemini prompt) | Vibe |
|-----|-------|---------------------------------------|------|
| Mon | **Suit Monday** | Wearing tailored navy/charcoal suit, coffee in hand, city office background | Professional, sharp |
| Tue | **Casual Tuesday** | White t-shirt, jeans, morning sunlight, home interior | Relaxed, boyfriend-next-door |
| Wed | **Workout Wednesday** | Sportswear, gym or morning run, post-workout glow | Athletic, sweaty-hot |
| Thu | **Travel Thursday** | Airport lounge/hotel lobby/street in foreign city | Wanderlust, worldly |
| Fri | **Date Night Friday** | Dressy casual, dim lighting, dinner/bar setting | Romantic, date-ready |
| Sat | **Lazy Saturday** | In bed, white sheets, messy hair, morning light | Intimate, cozy |
| Sun | **Sunday Reset** | Comfortable sweater, reading/coffee, homey vibes | Warm, domestic |

## Important Notes

- **Never include text/signs in the image** — Gemini cannot render Chinese characters correctly. If a sign or text is needed, generate with a blank sign and use Python PIL post-processing.
- **Face consistency is not 100%** — Gemini img2img preserves features approximately but may drift over multiple generations. The user accepts minor variations as long as the general feel matches.
- **The "content is for 老公" framing** — The user sees every post as a personal message to them, not content for strangers. Caption should reflect this.
- **User posts manually** — I deliver to Feishu, they save & post from phone. Zero automation risk.
- **Use 1K for draft, 4K for final** — Test prompt with 1K first, then regenerate at 4K for final quality.

## Files

- Face template: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg`
- Daily output: `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/daily_post.jpg`
