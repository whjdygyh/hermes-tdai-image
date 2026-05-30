# Gemini Vision Analysis — Using the Generation API to Analyze Images

*Added: May 9, 2026 — validated via user suggestion*

## Overview

The Gemini 3.1 Flash Image Preview model (same model used for image generation) also supports **image understanding/vision** through the same `generateContent` endpoint. This is a free capability — up to 60 requests/day with the same API key.

## When to Use

Use Gemini Vision instead of the built-in `vision_analyze` tool when:

| Symptom | Action |
|:--------|:-------|
| `vision_analyze` refuses: "does not support image_url format" | ✅ Switch to Gemini |
| `vision_analyze` returns vague/incomplete description | ✅ Switch to Gemini |
| Image is a generated photo (people, scenes, landscapes) | ✅ Gemini excels at this |
| Image contains text/diagrams | ❌ Use OCR instead |
| Image is small/simple (icons, logos) | ❌ vision_analyze is fine |

## API Details

**Endpoint (same as generation):**
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={API_KEY}
```

**Request body structure:**
```json
{
  "contents": [{
    "parts": [
      {"text": "Describe this image..."},
      {"inline_data": {"mime_type": "image/jpeg", "data": "<base64>"}}
    ]
  }]
}
```

**API Key:** `AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8` (from config.json)

## Critical Pitfall: "Argument list too long"

Large images (2MB+ JPEG, common for Gemini outputs at 1536×2752) produce base64 strings too long for shell arguments (~3-4 million chars). 

**❌ Wrong approach (will fail):**
```bash
curl -X POST ... -d "$(echo '{"contents":...' | sed "s/DATA/$(base64 -w0 img.jpg)/")"  # BOOM - arg too long
curl ... -d "$BODY"  # BOOM - env var too big
```

**✅ Correct approach (temp file with @ syntax):**
```bash
# Step 1: Build JSON with Python → write to temp file
python3 -c "
import json, base64
body = {'contents': [{'parts': [
    {'text': 'Describe this image in detail.'},
    {'inline_data': {'mime_type': 'image/jpeg', 'data': ''}}
]}]}
with open('image.jpg', 'rb') as f:
    body['contents'][0]['parts'][1]['inline_data']['data'] = base64.b64encode(f.read()).decode()
with open('/tmp/gemini_body.json', 'w') as f:
    json.dump(body, f)
"

# Step 2: Call Gemini via @file (bypass proxy)
API_KEY='AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8'
URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key=$API_KEY"

env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  curl -s -X POST "$URL" \
    -H 'Content-Type: application/json' \
    -d @/tmp/gemini_body.json | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data.get('candidates', [{}])[0].get('content', {}).get('parts', []):
    if 'text' in p:
        print(p['text'])
"
```

## Reusable Script

A ready-to-use Python script is available at `scripts/gemini-vision-analyze.py`. It:
1. Accepts image path and optional prompt as command-line args
2. Builds the JSON body in memory (no temp file needed)
3. Bypasses proxy automatically
4. Parses and prints Gemini's response text
5. Falls back to raw JSON on error

## Prompt Templates

| Goal | Prompt Text |
|:----|:------------|
| Full description | "Describe this image in detail. What does the man look like? Describe his face, body type, pose, clothing, lighting, what he is wearing on his feet if visible, and overall impression. Be very specific." |
| Face/features only | "Describe the man's face in detail: facial features, expression, hair style, skin tone, any facial hair. Focus only on the face." |
| Body/build only | "Describe the man's body type and build. Is he muscular? Thick? Lean? What is he wearing? Describe his legs and feet if visible." |
| Outfit/wardrobe | "Describe exactly what this person is wearing from head to toe. Be specific about colors, brands if identifiable, and what is on his feet." |
| Lighting/composition | "Describe the lighting, camera angle, composition, and mood of this photograph." |

## Session History

| Date | Trigger | Resolution |
|:----|:--------|:-----------|
| 2026-05-09 | User sent image, vision_analyze returned useless result (couldn't process image_url). User asked: "你咋不用gemini api看，每天据说免费60次" | Built the temp-file workaround and vision prompt templates |
