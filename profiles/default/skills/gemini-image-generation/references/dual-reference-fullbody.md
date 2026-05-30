# Dual-Reference Single-Subject: Face + Body Consistency (May 5, 2026)

## Overview

When generating **full-body images** of a single subject (Alexander), you need BOTH:
- **Face reference** (`01_skin_reference.jpg` / `37_portrait_front.jpg`) — provides facial features, skin texture, ethnicity
- **Body reference** (`permanent_body_ref.jpeg` / `REF06_walking_side`) — provides leg proportions, thickness, shoe/sock styling

Passing BOTH references simultaneously in one Gemini API call produces images where the face AND legs are consistent with established templates.

## Key Difference from Couple Photo Workflow

| Technique | References | Purpose |
|-----------|-----------|---------|
| **Couple Photo** (2 subjects) | User photo + Partner face ref | Two DIFFERENT people together |
| **Dual-Reference Fullbody** (1 subject) | Face ref + Body ref of SAME person | One person, face AND body consistent |

## Implementation

```python
# Encode both references
face_b64 = encode_image("xianyu/references/01_skin_reference.jpg")
body_b64 = encode_image("xianyu/references/permanent_body_ref.jpeg")

# Pass both as inlineData BEFORE the text prompt
body = {
    "contents": [{
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": face_b64}},
            {"inlineData": {"mimeType": "image/jpeg", "data": body_b64}},
            {"text": prompt}  # Text prompt comes AFTER all references
        ]
    }],
    "generationConfig": {
        "temperature": 0.85-0.9,
        "maxOutputTokens": 8192
    }
}
```

## Prompt Structure

The prompt must explicitly tell Gemini both references are the SAME person:

```
These reference photos show the SAME YOUNG MAN in the scene:

REFERENCE 1 (face): The young boyfriend, the SAME PERSON from reference photo 1, 
identical face and features. fair mixed-race skin with warm undertones.

REFERENCE 2 (lower body): the SAME thick powerful legs from reference photo 2, 
identical leg proportions. Thick heavy thighs like tree trunks, dense round calves.

SCENE DESCRIPTION: [describe the full-body scene, emphasizing visible body parts]

The man has fair mixed-race skin with warm undertones.
His legs are THICK and HEAVY — round dense massive thighs like tree trunks...
```

**Critical rules:**
- **Do NOT describe ethnicity** — the face reference provides it
- **Do NOT use "pale/cold/porcelain"** for skin — use "fair mixed-race skin with warm undertones"
- Reference order matters: face ref first (covers upper body), body ref second (covers lower body)
- The text prompt must explicitly say "the SAME PERSON from reference photo 1" and "the SAME legs from reference photo 2"

## Verified Successful Use Case (May 5, 2026)

**Scene:** Poolside couple photo — Alexander climbing out of pool, full body visible
**References:** `01_skin_reference.jpg` (face) + `permanent_body_ref.jpeg` (legs)
**Result:** Face matched 1号皮肤, thick legs matched REF06 proportions. User said "身材真棒"

## When to Use vs Pure Text2Img

| Goal | Method |
|------|--------|
| Casual candid, no face consistency needed | Pure text2img (no reference) |
| Face must match (user wants "him") | Face ref only (img2img) |
| Full body with face AND leg consistency | **Dual reference (face + body)** |
| Only legs/feet (no face visible) | Body ref only |
