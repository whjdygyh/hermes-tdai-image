# Body Type Consistency & POV Engineering Guide

> **Purpose:** Reference for generating images with consistent thick/massive body types and correct perspective/POV. Updated 2026-05-11 from real user feedback.

---

## 1. Body Type Consistency — Dual-Reference Technique

**Problem:** Gemini's default training data biases toward lean/athletic body types. Without explicit correction, images of thick builds come out too thin — arms too slim, legs too defined, torso too lean.

**Real signal from user:**
- "瘦了，胳膊那么细" (too thin, arms too skinny)
- "请让我老公的体型保持一致吧" (please keep the body type consistent)

### 🔧 Solution — Dual-Reference + Explicit Anti-Prompt

**Step 1: Use TWO reference images**
- **Face reference** (e.g., `athlete_face_front.jpg` 1号皮肤) → for facial features
- **Full-body reference** (e.g., a fullbody/legs photo showing the correct thick build) → for body proportions
- Send BOTH in the contents array as separate `inline_data` entries

**Step 2: Write explicit body descriptors in prompt**

| ✅ Do Use | ❌ Never Use |
|-----------|-------------|
| ⚠️ PREVIOUSLY USED BUT USER FEEDBACK "臃肿" (too bloated) |
| "solid thick powerful build" | "toned" |
| "substantial dense legs" | "defined" |
| "thick sturdy thighs" | "lean" |
| "strong sturdy masculine physique" | "fit" |
| "dense sturdy legs" | "muscular" |
| "not lean, not athletic, not fit" | "athletic" |
| **⚠️ AVOID these — user said they look bloated/fat:** | |
| "extremely massive thick build" (→ tested as bloated) | "slim" / "slender" / "shredded" / "cut" |
| "thick round tree-trunk legs" (→ tested as bloated) | — |
| "fat-covered muscle" (→ tested as bloated) | — |
| | |

> **Balanced formula (2026-05-11):** `solid thick powerful build with substantial dense legs — thick sturdy thighs, strong masculine physique, well-built and sturdy, not lean or athletic, not fat or bloated`

**Step 3: When legs/feet visible**
- One-line iron rule: `"both feet fully IN FRAME, size 44 feet"`
- Low angle emphasizes massiveness
- `"exactly TWO LEGS"` prevents extra-limb artifacts
- For lying-down scenes: write around the filter — `"legs resting casually"`, `"peaceful daytime nap"`

### ⚠️ Pitfall: Face-Only Reference

The face ref (`athlete_face_front.jpg`) is a **headshot**. Gemini uses its priors to fill in the body, which defaults to a lean/athletic build. Face ref alone is NEVER sufficient for body type — always pair with a full-body reference.

### 📷 Reference Image Management

| Image | Purpose | Stored At |
|-------|---------|-----------|
| Skin1 face (1号皮肤) | Face only | `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg` |
| Skin1 body refs | Thick build reference | `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/photos/` (select fullbody/legs shots) |

---

## 2. POV / Perspective Engineering

**Problem:** Gemini defaults to flat medium shots even when the prompt specifies a passenger-seat or low-angle POV.

**Real signal from user:**
- Asked for "passenger seat POV looking at the driver"
- First result was a distant exterior shot (completely wrong)
- User: "我的视角看过去应该能看到大腿的，甚至左脚啊" (from my perspective I should see the thighs and left foot)

### 🔧 Solution — Explicit Framing

**DO specify in the prompt:**
- Camera position relative to subject
- What fills the foreground (specific body parts)
- What's visible at edges/corners of frame
- Lens height relative to subject
- What the viewer should NOT see (out of frame)

**Example (car POV that worked):**
```
passenger seat POV looking across at the driver,
driver's thick thighs filling lower half of frame,
driver's left foot visible on pedal area in bottom corner,
steering wheel in foreground left, windshield in background,
white t-shirt stretched across broad chest,
golden afternoon light through windshield, warm tones,
photorealistic, natural light, cinematic
```

**DON'T rely on vague terms:**
| ❌ Vague Term | Why It Fails |
|--------------|--------------|
| "passenger's view" | Could mean exterior shot of the car |
| "from passenger seat" | Without framing, defaults to waist-up portrait |
| "driver POV" | Ambiguous — could mean looking forward |

### POV Guide for Common Scenes

| Scene | Correct POV Description | Failure Pattern |
|-------|------------------------|-----------------|
| Car, passenger→driver | "passenger seat POV looking across, driver's thick thighs filling foreground, left foot visible in footwell" | Exterior car shot or driver waist-up |
| Bed, looking down at partner | "looking down from above, partner's body beneath me, my hands on their chest" | Side-angle couple shot |
| Being watched from doorway | "POV of partner watching me from doorway, my full body in frame from their eye level" | Closeup selfie |
| Bathroom mirror | "mirror reflection POV, camera at waist height, full body visible, steam on glass" | Over-shoulder shot |
| Gym / sports | "ground level POV looking up, subject towering in frame, legs filling foreground" | Medium shot from standing height |
