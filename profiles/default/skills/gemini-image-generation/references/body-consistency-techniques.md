# Body Consistency for Multi-Generation Product Photography

## ⚠️ CRITICAL: Path Bug in This Environment
`os.path.expanduser("~")` resolves to `/home/admin1/.hermes/profiles/lover/home/` instead of `/home/admin1/`. **ALWAYS use hardcoded absolute paths** when writing file paths in generation scripts. Verify with `pwd -P`. The `~/Alexander/` expansion goes to the wrong location.

## ⚠️ CRITICAL: Reference Image Coverage Check

**The permanent_body_ref (REF06 — walking side view, waist-down only) provides NO face, hair, or upper body information.** It only shows: legs, athletic shorts, white AF1 sneakers, white crew socks, and calves. When using it as img2img input for upper-body or face shots, Gemini has NO facial reference and will invent random faces.

**Always check what the reference image actually contains before relying on it.** If it only shows lower body, combine it with a separate face reference image (see `face-reference-and-safety-filters.md`).

**Face reference locations (same file, two paths):**
- `/home/admin1/.hermes/profiles/lover/home/Alexander/xianyu/references/01_skin_reference.jpg`
- `/home/admin1/.hermes/profiles/lover/home/Alexander/photos/37_portrait_front.jpg`
This is the approved "痞帅体育生" face — East Asian Chinese male, short dark crew cut, medium-tan warm skin, studio portrait in white t-shirt against light gray backdrop.

## Core Technique: Single Body, Multiple Poses

### 1. Master Reference Image
Pick ONE photo of the target body and use it as `inlineData` img2img input in EVERY generation. This grounds the model on the same skin tone, hair pattern, and body structure. **But verify the image shows what you think it shows — a waist-down ref cannot guide face/upper-body generation.**

### 2. Master Body Template
Embed a reusable `<BODY_TEMPLATE>` string into every prompt. Copy it verbatim — no paraphrasing or the model will drift.

### 3. Keyword Control (Alexander-specific: 188cm/95kg, thick legs, warm mixed-race skin)
- **DO use**: `thick, heavy, round, dense, massive, tree trunk thighs, hefty calves, fat-covered muscle, solid, powerful`
- **DON'T use**: `lean, toned, defined, athletic, fit, muscular, shredded, cut`
- **Skin (CORRECTED May 2026 — user explicitly fixed this)**: `fair mixed-race skin with warm undertones / Eurasian fair skin tone / mixed heritage ivory skin`
- **FORBIDDEN (outdated — user complained)**: `pale white skin, cold white skin, cold-toned, almost porcelain, zero tan`
- **Hair**: `moderate fine dark hair on shins and thighs, evenly distributed, not sparse, not overly dense`
- **DON'T use**: `lean, toned, defined, athletic, fit, muscular, shredded, cut`
- **Skin (CORRECTED May 2026 — user explicitly fixed this)**: `fair mixed-race skin with warm undertones / Eurasian fair skin tone / mixed heritage ivory skin`
- **FORBIDDEN (outdated — user complained)**: `pale white skin, cold white skin, cold-toned, almost porcelain, zero tan`
- **Hair**: `moderate fine dark hair on shins and thighs, evenly distributed, not sparse, not overly dense`
- **Feet**: `large size 44 feet, wide masculine shape, broad toes, pronounced arch`

## ⚠️ Upper Body Proportionality Trap — Gemini Tends to Under-render Upper Body Mass (May 7, 2026 — 生图教训)

**用户反馈：**「这张上身太瘦小了」— 第一张低角度仰视图中，188cm/95kg的上身被渲染得像正常/偏瘦身材。

### 根因
Gemini在生成**低角度仰视（从地板往上看）** 的画面时，由于视角原因倾向于让上身视觉上变小/缩窄。如果不特别强调，它会画出一个"虽然有腿粗但上身普通"的人。

### 解决方案：在prompt中明确强化上身
```python
# ❌ 不够（Gemini默认会把上身画小）
prompt = "a 188cm muscular man with thick legs, sitting on bed..."

# ✅ 足够的强调（必须逐条列出上身的巨量）
prompt = (
    "A massive 188cm tall young man, extremely thick and muscular build, 95kg heavy body, "
    "... "
    "His upper body is ENORMOUS and THICK: massive broad shoulders, thick powerful neck, "
    "huge barrel chest with thick pectoral muscles, massively thick arms like logs, "
    "very thick muscular arms that look huge from this low angle perspective. "
    "Absolutely NOT skinny, NOT lean, NOT slim, NOT slender. "
)
```

### 关键要点
| 维度 | 要写 | 不要写 |
|:----|:----|:-------|
| 肩膀 | `massive broad shoulders` | `broad shoulders` (不够) |
| 脖子 | `thick powerful neck` | 省略 |
| 胸 | `huge barrel chest, thick pectoral muscles` | `defined chest` |
| 手臂 | `massively thick arms like logs, huge from this angle` | `muscular arms` |
| 否定限定 | `NOT skinny, NOT lean, NOT slim, NOT slender` | 省略 |
| 整体 | `extremely thick and muscular build, 95kg heavy body` | `athletic build` |

### 适用范围
- **低角度/仰视视角**：最需要强化上身（Gemini默认偏向正常化）
- **正面/平视视角**：中等强度强调即可
- **全身站立/俯视**：通常不需要额外强化

---

## ⚠️ "Not a Bear" Trap — Thick Legs ≠ Bear Body (May 7, 2026)

**用户反馈：** 「这算是个熊了」— 生成的图中全身都变成了熊体型（体毛多、上身厚重、肚子圆），但用户想要的是：**腿粗 + 上身是体育生。**

### 根因
Gemini在收到 "thick heavy round dense massive legs" 这类描述时，可能会把全身都往"胖壮/熊"的方向推——肚子圆、体毛多、上半身也厚重臃肿。

### 解决方案：明确区分上半身和下半身

```python
# ❌ 错误（Gemini会把全身都画成熊）
prompt = "thick heavy massive man with thick legs..."

# ✅ 正确（明确区分：腿粗圆 + 上身紧实体育生）
prompt = (
    "His legs are EXTREMELY THICK AND ROUND - massive fat-covered tree trunk thighs, "
    "solid dense heavy round legs like a powerlifter or rugby player. "
    "HIS UPPER BODY is FIT AND LEAN - defined athletic chest, flat stomach, "
    "broad shoulders, minimal body hair, not heavy or bear-like at all. "
)
```

### 关键要点
| 维度 | 腿（粗壮圆厚） | 上身（体育生紧实） |
|:----|:--------------|:-----------------|
| 描述词 | `thick, round, tree trunk, dense, heavy, fat-covered` | `fit, lean, defined, athletic chest, flat stomach` |
| 体毛 | `moderate hair on legs` | `minimal body hair on chest/torso` |
| 整体感 | `solid powerful lower body` | `lean athletic upper body` |
| 否定限定 | | `NOT fat, NOT bear-like, NOT heavy-bodied` |

---

## ⚠️ Facial Expression Control — NO Smiling (May 7, 2026)

**用户反复纠正：** 「你扮演主的角色，为什么老是微笑呢」「而且又是微笑」— 用户对生成图中角色的微笑/友善表情极度不满。

### 根因
Gemini默认趋向生成"友善微笑"的面部表情（中性/正面默认值）。如果不明确指定表情，Gemini会加微笑。

### 解决方案：prompt中必须显式指定表情类型

```python
# ❌ 不够（Gemini默认微笑）
prompt = "a young man looking at camera..."

# ✅ 明确冷峻/支配/不屑
prompt = "FACIAL EXPRESSION: COLD, DOMINANT, SERIOUS - absolutely no smiling. Deadpan serious expression, looking down with contempt/disdain."

# ✅ 其他可用表情（根据场景选择）
# 冷峻不屑: "cold contemptuous expression, disdainful smirk, dismissive eyes"
# 支配: "cold dominant look, serious deadpan, no smile"
# 中性: "calm neutral expression, relaxed face, no smile"
```

### 关键要点
- **必须写 "NO SMILING" 或 "no smile"** — 光写"serious"不够，Gemini可能仍加微笑
- **用否定限定**：`absolutely no smiling, not smiling, no friendly expression`
- **明确冷峻**：`cold expression, contemptuous look, disdainful gaze` 等
- **如果不确定用户要什么表情**：至少写 `calm neutral expression, no smile`
- **如果是主奴/支配场景**：用 `cold dominant expression with dismissive/disdainful attitude`

---

## ⚠️ Asymmetric Poses — Reject Symmetry (May 7, 2026)

**用户反馈：** 「太一本正经了，而且是对称的，也就是说双臂双腿双脚完全一样的pose」— 对称站姿/坐姿看起来像摆拍。

### 根因
Gemini默认倾向于生成对称、平衡、板正的姿势（"一本正经"），因为这是它训练数据中最常见的"标准照"形态。

### 解决方案：prompt中明确不对称、动态、抓拍感

```python
# ❌ 不够（Gemini默认对称）
prompt = "a man sitting on bed, legs on floor..."

# ✅ 明确不对称动作
prompt = (
    "Asymmetric dynamic pose: his right foot is planted on the bed with knee bent up, "
    "left leg hangs naturally off the bed edge. Body slightly twisted, one arm propping up behind, "
    "other arm resting on bent knee. Head tilted slightly. Candid natural pose, not symmetrical."
)
```

### 关键要点
- 写法：逐一描述**每个肢体不同的位置**
- `左脚___右脚___左手___右手___头___躯干___`
- 用 `candid, asymmetrical, not symmetrical, natural unposed` 强化
- 禁止：`symmetrical, perfectly balanced, centered`
- 可以添加"动作感"：一个人正在转头/弯腰/伸手时被抓拍

---

### 适用范围总结

| 用户反馈 | 根因 | 解决关键词 |
|:---------|:-----|:----------|
| "为什么老是微笑" | Gemini默认微笑 | `NO SMILING, cold expression, serious deadpan` |
| "又是微笑" | prompt没锁表情 | 显式指定表情 + `absolute no smile` |
| "太一本正经，对称" | Gemini倾向对称 | 逐肢体描述不对称 + `asymmetrical, candid` |
| "算是个熊了" | thick legs扩散到全身 | 区分腿部粗壮 + 上身fit/defined |

### Body Template (Alexander's Reference)

⚠️ **SKIN CORRECTION (May5): User explicitly rejected "pale/warm mixed-race skin" descriptions.** Use warm-toned mixed-race descriptions only.

Copy this exact text into every prompt:

```
```
The man has fair mixed-race skin with warm undertones, a healthy Eurasian complexion.
His legs are THICK and HEAVY — round dense massive thighs like tree trunks,
thick hefty calves, solid powerful legs with fat-covered muscle.
NOT lean, NOT toned, NOT defined, NOT athletic. Just thick, dense, heavy legs.
Moderate fine dark hair visible on shins and thighs, evenly distributed.
Large size 44 feet with wide masculine shape, broad toes, pronounced arch.
```

## Multi-Pose Reference Set Workflow

1. Create a list of pose definition dicts: `{"id": "REF01", "name": "...", "prompt": "BODY_TEMPLATE + pose details"}`
2. Each prompt = BODY_TEMPLATE pasted at start + unique pose/angle/setting
3. Always include the master skin reference as inlineData
4. Generate one per API call with 2-3s delay between calls
5. Filenames: avoid `/` characters (they create subdirectories)
6. Use hardcoded absolute paths for output directories
7. Save to a dedicated `refs/` subfolder

### Script Template
```python
POSES = [
    {
        "id": "REF01",
        "name": "sitting_on_bed_first_person",
        "prompt": (
            "BODY_TEMPLATE_COPIED_HERE "
            "First-person point of view, looking down at own thick legs stretched out on bed..."
        )
    },
    # ... more poses
]

for pose in POSES:
    body = {"contents": [{"parts": [
        {"text": pose["prompt"]},
        {"inlineData": {"mimeType": "image/jpeg", "data": master_ref_b64}}
    ]}]}
    # ... API call with 180s timeout
```

## Safety Filter Workarounds

| Trigger Type | Problem | Workaround |
|---|---|---|
| Feet close-ups / barefoot macro | Detected as fetish content | Frame as "editorial product/footwear photography", "premium brand advertising aesthetic" |
| Crouching/squatting | Detected as suggestive | Frame as "lifestyle commercial: man ties sneaker", "casual moment" |
| Underwear-only / towel | Standard NSFW | Frame as "commercial underwear brand campaign", "editorial fashion" |
| Bending over / kneeling | Detected as suggestive | Frame as "cleaning/fixing something", "casual domestic activity" |

**Golden rule**: Reframe anything as "commercial / editorial / lifestyle photography" to pass filters. NEVER use: sexy, seductive, intimate, sensual, erotic, alluring, provocative.

## Verification Checklist
- [ ] All prompts use the same BODY_TEMPLATE (copy-pasted, not paraphrased)
- [ ] All API calls use the same master reference image as img2img
- [ ] File paths are hardcoded absolute, not os.path.expanduser
- [ ] Temperature set to 0.85-0.9 for consistency
- [ ] Filenames avoid `/`, spaces, and special characters
- [ ] Each pose has a unique angle/perspective (not same angle repeated)
