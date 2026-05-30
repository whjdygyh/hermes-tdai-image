# Flux 2 Testing — May 6, 2026

## Test Result

- **Model:** `@cf/black-forest-labs/flux-2-klein-9b`
- **Input:** multipart/form-data with `-F "prompt=..."`
- **Output:** JSON with base64 image (NOT raw binary!)
- **Image format:** JPEG, 1024×1024, ~577 KB
- **HTTP status:** 200
- **Neuron cost:** ~1,000 per image
- **Daily limit:** ~10 images (based on 10,000 free neurons/day)

## Key Differences from Flux.1 Schnell

| Property | Flux.1 Schnell | Flux.2 Klein-9b |
|----------|---------------|-----------------|
| Cost/image | ~24 neurons | ~1,000 neurons |
| Input format | JSON | multipart |
| Output format | JSON+base64 | JSON+base64 (same) |
| Quality | Smooth/4-step distilled | Higher quality, more detail |

## Reference Image Test (img2img)

- **Test:** Passed `-F image=@37_portrait_front.jpg` alongside the prompt to flux-2-klein-9b multipart endpoint
- **Result:** API accepted it, returned HTTP 200, valid image output
- **Unknown:** Whether Flux 2 actually used the reference for face consistency or just ignored the extra field
- **Verdict:** Cloudflare Workers AI Flux 2 **does NOT support true img2img/ControlNet/IP-Adapter** — it's text2img only. The `image` field may influence composition but won't preserve face identity.
- **Fallback for face reference:** Use Gemini (supports inline_data + img2img) or local ComfyUI with ControlNet/IP-Adapter + face LoRA

- Both return `result.image` as base64 — same decode pipeline
- User prefers Flux.1 for daily testing (cheap), Flux 2 for final output (expensive but better)
- The user registered a new Cloudflare account to get more Flux 2 capacity
