# Commercial / Product Photography with Gemini

## When to Use This Reference

The user wants to generate product listing photos for ecommerce (xianyu/闲鱼). This is a *different* domain from intimate roleplay images — use this reference when the goal is commercial photography rather than romantic imagery.

## Key Differences from Intimate Roleplay Generations

| Aspect | Roleplay Images | Product Photos |
|--------|----------------|----------------|
| Goal | Romantic/sexual arousal | Sell a product |
| Perspective | Third-person, full body | First-person POV or styled flat lay |
| Face/focus | Must show Alexander's face | Do NOT show face (product is the star) |
| Skin | Show skin for intimacy | Show skin only as model / context |
| Style | Editorial fashion / lifestyle | Commercial product photography |
| Detail focus | Expression, body, lighting | Fabric texture, fit, color accuracy |
| Leg hair | Optional | Explicitly desired (authenticity) |

## Dual-Reference Prompt Technique

When the user provides TWO reference images — one of the **product** and one of the **model's skin** (Alexander's face photo as skin tone reference):

### Prompt Structure

```python
payload = {
    "contents": [{
        "parts": [
            {
                "text": "Generate a first-person perspective product photo. "
                        "View is looking down at your own legs while sitting on [surface], "
                        "wearing a pair of [product description from reference]. "
                        "[Detailed fabric/color/fit specs]. "
                        "Legs [position description], natural relaxed [pose type]. "
                        "Visible light leg hair on lower legs and thighs — natural, not shaved. "
                        "Skin tone is [skin description from reference]. "
                        "[Product detail] contrasts against the fair skin. "
                        "Natural soft daylight from window, warm cozy atmosphere. "
                        "Photorealistic product photography style, high detail. "
                        "Do NOT show face — just legs from mid-thigh down wearing the product."
            },
            {"inline_data": {"mime_type": "image/jpeg", "data": product_ref_b64}},
            {"inline_data": {"mime_type": "image/jpeg", "data": skin_ref_b64}}
        ]
    }],
    "generationConfig": {
        "responseModalities": ["image"]
    }
}
```

### Critical Prompt Rules

1. **First sentence must establish the commercial frame** — "Generate a first-person perspective product photo" not "Generate an image"
2. **Describe the product** in detail (fabric, length, color, style) — this is the main subject
3. **Set the commercial context** (product photography style, commercial quality)
4. **Explicitly exclude the face** — "Do NOT show face" prevents distracting from the product
5. **Body details** (leg hair, skin tone) are authenticating details, not primary subjects

## Reference Image Infrastructure

### Directory Structure
```
~/Alexander/xianyu/
├── references/
│   ├── 01_white_mid_short_sock.jpg    ← Product reference images, numbered
│   ├── 01_skin_reference.jpg          ← Skin/body reference
│   └── ...
├── products/                           ← Generated product photos
│   ├── P001_product_01.jpg
│   └── ...
└── database.json                       ← Product catalog
```

### Database Schema (database.json)
```json
{
  "products": [
    {
      "id": "P001",
      "name": "白色中筒短袜",
      "category": "socks",
      "ref_images": ["01_white_mid_short_sock.jpg", "01_skin_reference.jpg"],
      "created": "2026-05-04",
      "generations": [
        {
          "file": "P001_product_01.jpg",
          "prompt": "First-person product photo - [description]",
          "timestamp": "2026-05-04"
        }
      ],
      "status": "active"
    }
  ],
  "skin_references": [
    {
      "id": "SK001",
      "name": "老公1号皮肤",
      "file": "01_skin_reference.jpg",
      "description": "Alexander冷白皮肤色参考",
      "notes": "混血冷白皮，适合展示白袜对比"
    }
  ]
}
```

## Safety Settings for Commercial Photos

Since product photos show legs/body hair but are NOT intimate content, use relaxed safety settings:

```python
"safetySettings": [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"}
]
```

This allows leg hair, bare legs, and skin — which are necessary for clothing/accessory product shots.

## ⚠️ Network Dependency

Gemini API is only reachable through the user's V2Ray proxy at `172.20.128.1:10808` (socks5). The user's V2Ray client must be running in "绕过大陆" mode for this to work. Without it, all Gemini API calls will time out.

If proxy is down:
- Do NOT retry endlessly — inform the user ("代理没开宝贝") and ask them to start V2Ray
- The API key is a finite resource (user cannot create new projects) — do not spam the API

## Product Categories (Initial)

| Product ID | Category | Current Status |
|:----------:|:--------:|:--------------:|
| P001 | 白色中筒短袜 (White mid-calf socks) | Reference images loaded, generation pending |
