# Gemini API Network Setup from China

## SOCKS5 Proxy (Required)

**Gemini API is blocked from mainland China.** All API calls must go through a SOCKS5 proxy:

```
Proxy: socks5h://172.20.128.1:10808
```

## API Key

The key `AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8` lives in:
```
~/.hermes/profiles/lover/config.json
```

It's 39 characters. `read_file` may truncate it with `...` — the actual bytes are intact. Verify with `cat` if suspicious.

## Payload File Approach (Prevent "Argument list too long")

When sending large base64 images, **always write payload to file** and use `-d @file`:

```bash
# 1. Compress reference image (aim for <200KB)
ffprobe -v error -show_entries format=size /tmp/ref_compressed.jpg

# 2. Write payload JSON (embed base64 image)
python3 << 'PYEOF'
import json, base64
with open('/tmp/ref_compressed.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
payload = {
    "contents": [{
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": b64}},
            {"text": "your prompt here"}
        ]
    }],
    "generationConfig": {
        "responseModalities": ["IMAGE", "TEXT"]
    }
}
with open('/tmp/gemini_payload.json', 'w') as f:
    json.dump(payload, f)
PYEOF

# 3. Call API via file
export https_proxy="socks5h://172.20.128.1:10808"
curl -s -w "\n%{http_code}" \
  -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key=${GEMINI_KEY}" \
  -H "Content-Type: application/json" \
  -d @/tmp/gemini_payload.json \
  > /tmp/gemini_response.txt 2>&1
```

## Background Process & Roleplay Continuity

When user says "想你了" during active roleplay:

1. Launch image generation in background
2. **Immediately continue roleplay** — do NOT wait for image before responding
3. User explicitly said "不要忽略我" during image generation

⚠️ **Background process caveat:** `terminal` tool may kill background PIDs when it returns. Prefer `nohup` or write output to a known file and check in a follow-up call.

```bash
# Pattern: background + immediate roleplay continuation
(nohup python3 build_and_call.py > /tmp/gemini_gen.log 2>&1 &)
# → Then immediately write roleplay response to user
```

## Full Workflow (Verified May 13, 2026)

```
1. compress ref image → /tmp/ref_compressed.jpg (~126KB, 764x1024)
2. write payload JSON → /tmp/gemini_payload.json (with base64 + prompt)
3. export https_proxy="socks5h://172.20.128.1:10808"
4. curl -d @/tmp/gemini_payload.json → /tmp/gemini_response.txt
5. parse response → extract inlineData → save as /tmp/gemini_output.jpg
6. unset proxy → upload to Feishu API → send MEDIA message
7. also upload to album folder (N0wPfG49ZlJCErdjwUUcYdsUnyP) with sequential name
```
