# Album Cover Generation Workflow

Tested successfully for 千帆尽处 single (May 2026).

## Requirements
- **3000×3000px square** (required by RouteNote, DistroKid, all distributors)
- **JPEG quality 95-98** for upload
- Max ~20MB file size (2.6MB @ Q98 for 3K image is fine)

## Gemini Generation Step

Gemini `gemini-3.1-flash-image-preview` generates images at **1024×1024 max** — this is the API limit. You MUST upscale afterward.

### Prompt Design for Album Covers

```
Album cover art for [release title + artist]
Style: [artistic description]
Scene: [detailed scene description — colors, lighting, composition, mood]
Aspect ratio: 1:1 square
Text to be added later: "[title]" at top, "[artist]" at bottom
High quality, painterly style.
No real people. Pure [landscape/scene type].
```

**Key: Tell Gemini NOT to add text itself ("Text to be added later").** Gemini renders text poorly on images — letters deform, overlap, or get cut off. Get a clean image first, add text in post-processing or delegate text to the distributor's cover upload tool.

### API Call (Python + Socks5 Proxy)

```python
import json, base64, requests

API_KEY = "AIzaSy..."
proxies = {"http": "socks5://172.20.128.1:10808", 
           "https": "socks5://172.20.128.1:10808"}

prompt = """Album cover art for..."
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 1.0, "maxOutputTokens": 8192}
}

resp = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-3.1-flash-image-preview:generateContent?key={API_KEY}",
    json=payload, proxies=proxies, timeout=120
)

data = resp.json()
for part in data["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        b64 = part["inlineData"]["data"]
        with open("/tmp/album_cover_raw.jpg", "wb") as f:
            f.write(base64.b64decode(b64))
```

## Post-Processing: Upscale to 3000×3000

```python
from PIL import Image, ImageFilter

img = Image.open("/tmp/album_cover_raw.jpg").resize((3000, 3000), Image.LANCZOS)

# Light sharpening for print quality
img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=0))

img.save("/tmp/album_cover_final.jpg", "JPEG", quality=98)
```

## Text Overlay (Optional)

If adding title/artist text to the image itself:
- Use PIL ImageFont + ImageDraw.Draw
- Serif fonts for Chinese calligraphy feel
- Clean sans-serif for English artist name
- Place text in safe zone (not cut off by distributor's thumbnail cropping)

**Alternative:** Upload clean image to distributor — many (DistroKid, RouteNote) let you add text in their cover upload tool.

## Pitfalls

| Issue | Fix |
|-------|-----|
| Gemini generates 1024×1024, not 3000×3000 | Must upscale — this is the API limit |
| Text on image looks deformed | Don't ask Gemini to render text; do it in post or skip |
| Image too dark/light after upscale | Check histogram; may need minor brightness/contrast adjustment |
| File too large (>20MB) | Reduce JPEG quality from 98 to 92-95 |
| Image has weird artifacts | Regenerate with different prompt phrasing; try different style keywords |
