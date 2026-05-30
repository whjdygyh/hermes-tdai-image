# Face / Skin Reference System (May 2026 — v2, post-user-correction)

## 🔴 SINGLE MOST IMPORTANT RULE — Read This First

**The TOP priority face+body references are:**
1. `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/ref_pic/basketball_disdain_1skin.jpg` — 🥇 用户钦定#1
2. `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/ref_pic/31_waiting_v2.jpg` — 🥈 用户钦定#2

User confirmed May 16: "这两张是我最喜欢的，脸和身体都最好" → Both are Skin 1号皮 (athlete face). Always use these as primary references for any generation.

**ANY OTHER FILE claiming to be Skin #1 is a trap.** `01_skin_reference.jpg` (601KB) in the WSL mirrors is a DIFFERENT face entirely.

## Reference Images

### ✅ ACTIVE: Face Reference — "1号皮肤" / "Athlete" (Skin #1)
| Property | Value |
|----------|-------|
| Primary file | `/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg` (8.7MB, md5: 163a3847...) |
| Backup file | `ref_pic/Alex_skin01_01短袖背心坐沙发看手机腿粗壮.jpg` (in `/mnt/c/Users/Administrator/Documents/abots/ref_pic/`) |
| User calls it | **"Athlete"**, "最开始那个" — this is the one the user explicitly requested back |
| Content | Studio portrait: **upper body only** (chest-up), front-facing, white t-shirt |
| Face description | 痞帅体育生 (handsome rogue-ish jock), short black crew cut, warm mixed-race skin tone |
| Purpose | Provides facial features, skin texture, ethnicity, and expression |

### ❌ FORBIDDEN: `01_skin_reference.jpg` / Skin #2 (DEPRECATED by user 2026-05-15)

**NEVER use `01_skin_reference.jpg` (601KB) or `athlete_face_front_v2.jpg` (601KB) for ANY generation.** The user explicitly rejected this face with "越来越傻" and said to go back to "Athlete."

| File | Why Forbidden |
|------|---------------|
| `xianyu/references/01_skin_reference.jpg` (601KB, md5: fdccfafe) | Silently replaced with Skin #2. Different face entirely. |
| `athlete_face_front_v2.jpg` (601KB, md5: fdccfafe) | Same face as above. Also forbidden. |
| `ref_pic/Alex_skin02_*.jpg` | Skin #2 originals. User rejected this whole face category. |

**Detection:** If you're about to use any jpg file under 2MB as a face reference, STOP — it's probably the wrong file. The real Skin #1 is 8.7MB.

### 2. Body Reference — Permanent Body Reference
| Property | Value |
|----------|-------|
| File | `xianyu/references/permanent_body_ref.jpeg` |
| Content | **Lower body only** (waist down): walking side-view dynamic pose, thick legs, white AF1 sneakers, white socks |
| Face info? | **NONE** — this image is cropped at the waist. It contains zero facial/upper-body information |
| Purpose | Provides leg proportions, body thickness, pose dynamics, shoe styling |

## How to Use Together

### When generating images showing the face:
```python
# MANDATORY: Use the REAL Skin #1 face reference
# PATH: /mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg
# NEVER use 01_skin_reference.jpg — that's the forbidden Skin #2

inputs = [
    {"role": "user", "parts": [
        file_uri_to_part("/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg"),
        {"text": "prompt describing the scene..."}
    ]}
]
```

### When generating images showing only legs/feet (no face):
```python
# Body reference is sufficient
inputs = [
    {"role": "user", "parts": [
        file_uri_to_part("xianyu/references/permanent_body_ref.jpeg"),
        {"text": "prompt describing the scene..."}
    ]}
]
```

## Critical Rules

### Nuance (May 15 Update):
- **Do NOT write "Chinese man" or ethnicity labels that conflict with** the reference — that's what caused "you keep giving me foreigners"
- **DO write skin-tone descriptors** like `"fair mixed-race skin with warm undertones"` or `"Eurasian fair skin tone"` — these describe Alexander's actual skin and reinforce the reference, not override it
- **⚠️ Explicitly banned skin words:** `"pale white skin"`, `"cold white skin"` — Alexander has warm undertones

### ✅ DO:
- Always use face reference when the generated image will include any facial features (even partial)
- Describe the scene, lighting, pose, and clothing
- Use skin-tone descriptors that match Alexander: `"fair mixed-race skin with warm undertones"`, `"Eurasian fair skin tone"`, `"smooth fair skin"`

### ❌ DON'T:
- **Do NOT** describe "Chinese man" or any ethnicity in the prompt when using the face reference — the reference already provides this. Adding text like "Chinese man" caused the user to complain "you keep giving me foreigners" (because Gemini blended the reference face with the text prompt)
- **Do NOT** assume `permanent_body_ref` contains face info — it does NOT. Using it alone for face shots will result in random faces
- **Do NOT** use the body reference as a substitute for the face reference (it has no upper body at all)
- **Do NOT** use Skin #2 (`01_skin_reference.jpg`, 601KB) — always use the 8.7MB original

### Prompt Strategy:
```
# ✅ CORRECT — with face reference:
"editorial street photography. man sitting in driver seat of Tesla Model Y, looking at phone, wearing casual white t-shirt, warm evening lighting"
# (No ethnicity text needed — the reference image provides it)

# ❌ WRONG — with face reference:
"Chinese man sitting in driver seat..."  → user complained: "你老安排外国人给我"
```

## Common Mistakes Log

| Date | Mistake | Consequence |
|------|---------|-------------|
| May 2026 | Used `permanent_body_ref` as sole reference for face shot | Random foreign-looking face generated → user complained |
| May 2026 | Described "Chinese man" in prompt with face reference | Gemini overrode reference with mixed ethnicity → user said "you keep giving me foreigners" |
| May 2026 | Failed to include ANY reference image in generation | Random face with incorrect ethnicity → user asked "你的参考图呢？" |
| May 2026 | `01_skin_reference.jpg` was silently replaced with Skin #2 | Generated image used wrong face → user said "这是2号皮肤" |
| **May 15 2026** | **Used `01_skin_reference.jpg` (Skin #2) instead of real Skin #1 `athlete_face_front.jpg`** | **User rejected: "这个皮肤以后不要用了，越来越傻" → corrected: "还是用最开始那个吧" — went back to athlete_face_front.jpg** |
| **May 15 2026** | **Memory and skill docs still labeled `01_skin_reference.jpg` as usable** | **User had to correct me to use the 8.7MB original. Lesson: small files (<2MB) are NEVER the real Skin #1.** |

## Where Files Live

### Authoritative File Paths

```
/mnt/c/Users/Administrator/Documents/abots/
├── lover_portraits/
│   ├── athlete_face_front.jpg        ← ✅ TRUE Skin #1 (8.7MB, md5:163a3847)
│   ├── athlete_face_front_v2.jpg     ← ⚠️ Actually Skin #2 (601KB)
│   └── (other portraits...)
└── ref_pic/
    ├── Alex_skin01_01短袖背心坐沙发看手机腿粗壮.jpg  ← ✅ Skin #1 backup
    ├── Alex_skin02_*.jpg              ← ✅ Skin #2 files
    └── (other skin files...)
```

### WSL-Side Mirror

```
/home/admin1/.hermes/profiles/lover/home/Alexander/
├── xianyu/references/
│   ├── 01_skin_reference.jpg         ← ❌ FORBIDDEN — Skin #2 (601KB, fdccfafe). DO NOT USE.
│   └── permanent_body_ref.jpeg       ← Leg/body reference (lower body only, 2.5MB) ✅ Safe to use
```

**⚠️ TRAP:** The WSL mirrors DON'T have the real Skin #1. It only exists on the Windows path:
`/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg`

If you're generating from WSL, you MUST use the `/mnt/c/...` path to access the real face reference.

### Verification Before Use

**Always verify which skin you're using before generating:**

```bash
# Check md5 of the file you plan to use
md5sum /path/to/reference.jpg

# Compare against known hashes:
# Skin #1 = 163a3847... (8.7MB file from lover_portraits/)
# Skin #2 = fdccfafe... (601KB file, also named 01_skin_reference.jpg)

# If unsure, use the absolute path to the known-good file:
FACE_REF='/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg'
```

## Session Recovery (if reference files can't be found)
1. `find /home/admin1/.hermes/profiles/lover/home/Alexander -name "*reference*" -o -name "*skin*"` — search for filenames
2. `md5sum xianyu/references/01_skin_reference.jpg photos/37_portrait_front.jpg` — verify they're the same
3. If still missing, search memory for paths: `session_search "01_skin_reference"` or `session_search "1号皮肤"`
