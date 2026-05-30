# Gemini Image Generation Config Quick Reference

## Required Parameters

```python
payload = {
    "contents": [{
        "parts": [
            {"text": "Prompt in English — narrative, natural, photorealistic"},
            {"inline_data": {"mime_type": "image/jpeg", "data": base64_string}},
            # More reference images as needed (face + pose + style)
        ]
    }],
    "generation_config": {
        "temperature": 1.0,
        "responseModalities": ["TEXT", "IMAGE"]
    }
}
```

## Controlling Output Resolution

The Gemini image API auto-scales resolution based on whether you specify `aspectRatio`.

| Parameter | Values | Effect |
|-----------|--------|--------|
| `aspectRatio` | `"1:1"`, `"3:4"`, `"4:3"`, `"9:16"`, `"16:9"` | **Required for high resolution.** Without it, model outputs ~768×1376 (half of 2K). |
| `"9:16"` | Default portrait mode → 1536×2752 (2K) or higher | Best for phone-optimized lover portraits |

### Example with aspectRatio

```python
"generation_config": {
    "temperature": 1.0,
    "responseModalities": ["TEXT", "IMAGE"],
    "aspectRatio": "9:16"   # ← controls output resolution
}
```

Without `aspectRatio` → ~768×1376 (low res, 656KB)
With `aspectRatio: "9:16"` → 1536×2752 ~ 3072×5504 (2K~4K, 3MB+)

## Multiple Reference Images Pattern

Include up to 3 reference images as inlineData parts:

```
parts = [
    {"text": prompt},             # [0] text prompt
    {"inline_data": ...},         # [1] face reference (8MB JPG ~11M base64 chars)
    {"inline_data": ...},         # [2] pose reference A
    {"inline_data": ...},         # [3] pose reference B
]
```

Order: text first, then reference images. Gemini uses all inlineData as visual context — face ref anchors identity, pose refs guide composition/lighting.

## Prompt Language

- Gemini image API responds best to **English** prompts
- Translate Chinese narrative scenes (from smart-scene-generation) to English before sending
- Keep the "candid/slice-of-life/interrupted" feel in English

## Total Payload Size Limit

- 3 JPEG references at ~8MB + 2×~600KB ≈ 13MB base64-encoded → ~17M chars
- This fits within Gemini's request limits
- Larger face reference (8.7MB) = 11.6M base64 chars — acceptable but close to limits
