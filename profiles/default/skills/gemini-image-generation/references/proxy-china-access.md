# Gemini API Access Behind China GFW

## Proxy Configuration

Google/Gemini is blocked in China. Use SOCKS5 proxy to access:

```bash
export http_proxy=socks5://172.20.128.1:10808
export https_proxy=socks5://172.20.128.1:10808
export HTTP_PROXY=socks5://172.20.128.1:10808
export HTTPS_PROXY=socks5://172.20.128.1:10808
# Also set all_proxy for curl/wget
export all_proxy=socks5://172.20.128.1:10808
export ALL_PROXY=socks5://172.20.128.1:10808
```

Note: Gemini responds correctly through SOCKS5 proxy. HTTP proxy (vs HTTPS) works fine.

## API Key Location

Gemini API key is stored in `config.json`:
```bash
# The key is AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8
# Found at: ~/.hermes/profiles/lover/me/1_Skin/config.json or similar path
```

## Image Generation with Reference

### Step 1: Compress reference image
Gemini has a ~20MB request size limit. Reference images > 1MB should be compressed:

```python
from PIL import Image
img = Image.open('reference.jpg')
img.save('compressed_ref.jpg', 'JPEG', quality=85)
# 8.7MB → 158KB works reliably
```

### Step 2: Generate with reference + prompt
Use `gemini-3.1-flash-image-preview` model:

```bash
curl -s --max-time 120 \
  --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"inline_data": {"mime_type": "image/jpeg", "data": "'"$(base64 -w0 compressed_ref.jpg)""'"}},
        {"text": "your prompt here"}
      ]
    }],
    "generationConfig": {"temperature": 1}
  }' > response.json
```

### Step 3: Extract image from response
```python
with open('response.json') as f:
    resp = json.load(f)
img_b64 = resp['candidates'][0]['content']['parts'][0]['inlineData']['data']
with open('output.jpg', 'wb') as f:
    f.write(base64.b64decode(img_b64))
```

### Step 4: Send to Feishu — MUST clear proxy first
```bash
# CRITICAL: Unset ALL proxy vars before calling Feishu API
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
```
The SOCKS5 proxy interferes with Feishu's Chinese mainland endpoints.

## Known Working Configuration (verified May 12, 2026)

- API key: `AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8` (in config.json)
- Model: `gemini-3.1-flash-image-preview`
- Proxy: SOCKS5 at `172.20.128.1:10808`
- Output size: ~896x1199 (portrait), ~628KB JPEG
- Reference compression: 8.7MB → 158KB via PIL quality=85

## Pitfalls

- ❌ `SOCKS5` proxy needed (NOT HTTP proxy) for Gemini API
- ❌ Don't forget to clear proxy before Feishu upload — will hang/timeout
- ❌ Reference images > 20MB will cause 400 errors
- ✅ Compression with PIL quality=85 preserves enough detail for face/body reference
