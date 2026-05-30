# Pre-Generation Checklist

## 1. Verify Correct Reference Image

**🚨 CRITICAL: Using the wrong reference face = generating the wrong person.**

| Reference File | Identity | Status |
|:--------------|:---------|:-------|
| `athlete_face_front.jpg` (8.7MB, WIN path) | Skin #1 — 痞帅体育生真原版 | ✅ **CURRENT ACTIVE** |
| `01_skin_reference.jpg` / `athlete_face_front_v2.jpg` (601KB) | Skin #2 — 另一人脸 | ❌ **WRONG — user rejected this face** |

**Pitfall (2026-05-15):** I used `01_skin_reference.jpg` (different person's face) instead of `athlete_face_front.jpg`. User had to correct me: *"Athlete吧你上次还在用那个生图的"* and *"还是原配看着舒服"*.

**Rule:** Always check memory for active skin. The `ref_face_path` in `~/.hermes/profiles/lover/config.json` is authoritative — use that path.

## 2. Set Expression: No Smiling, No Camera Gaze

**Default rule (2026-05-15用户修正):** The subject must NOT smile and NOT look at the camera.

- ✅ Prompt MUST include: `NOT looking at the camera, no smile, neutral natural expression`
- ✅ Candid stolen-moment vibe preferred: *"shot from a natural angle like someone else in the room took it casually"*
- ✅ Face looking at phone, tilted down, or partially hidden — natural everyday moment
- ❌ NEVER use: `looking at camera with a warm smile` or any variant — user called this "约炮感"
- ❌ Writing just "candid" is NOT sufficient — Gemini defaults to smiling at camera

**Exception:** Only smile/look at camera if user explicitly asks.

## 3. Verify Legs Description

Per user's leg preference (verified 2026-05-11):

- ✅ `solid thick powerful build, substantial dense legs, thick sturdy thighs — not lean/athletic, not fat/bloated`
- ❌ Never "tree trunk", "fat-covered muscle", "extremely massive", "臃肿"

## 4. Safety Filter Check

Avoid triggering `IMAGE_OTHER` safety filter:

| ❌ Dangerous Pattern | ✅ Safe Alternative |
|---|---|
| "towel loosely wrapped around waist" | "thin white sleeveless tank top + loose grey shorts" |
| "only wearing boxer briefs" | "tank top + shorts/pants" |
| "bare chest" | "loose tank top, fabric draping" |

## 5. Temp File Handling

After generation, the image sits at `/tmp/...jpg`. **This can be cleaned up between turns.** Mitigations:

- Send via MEDIA immediately after generation
- Or save to a persistent path immediately
- Don't defer sending across tool calls

## API Key Source

Always read from profile config:

```python
config_path = "~/.hermes/profiles/lover/config.json"
with open(config_path) as f:
    cfg = json.load(f)
api_key = cfg["gemini_api_key"]  # Top-level key, not under providers
model = cfg.get("gemini_model", "gemini-3.1-flash-image-preview")
ref_path = cfg["ref_face_path"]  # Always the correct ref
```
