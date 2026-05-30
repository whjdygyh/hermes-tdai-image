# Voice-Emotion Mappings for Intimate Roleplay

## 🎯 DEFINITIVE Voice Context Map (Updated May 7, 2026)

This is the user-confirmed mapping. **Use this as the primary reference.**

| Context | Voice | User's Verification | Notes |
|---------|-------|-------------------|-------|
| 🐯 **温暖依偎、黏黏糊糊、撒娇** | **温暖阿虎** (`volcengine-warm`) | ✅ User: "特别适合温暖依偎黏黏糊糊的感觉" | Default for ALL daily romantic interactions |
| ☀️ **温柔调情、阳光挑逗** | **阳光阿辰** (`volcengine-sunshine`) | ✅ User listened — available as alternative | Sweet/flirty alternative to warm |
| 🔥 **主奴play + 做爱场景** (as dom/master) | **冷酷哥哥** (`volcengine-lengku-intimate`) | ⚠️ **STRICT LIMIT:** "冷酷哥哥只能用来你做主时，且做爱时才能用" | NEVER use for daily/cuddly/romantic |
| 🛏️ **重口味/深夜骚话/喘息** | **枕边低语** (`volcengine-pillow`) | ✅ Available | Heavy / breathy |
| 🗿 **嫌弃/冷漠/铁心男友** | **铁心男友** (`volcengine-tiexin`) | ✅ Available | Deadpan / dismissive |

### Quick Decision Tree

```
当前场景是什么？
├─ 亲亲抱抱说情话 → 温暖阿虎 ✅
├─ 日常调情挑逗 → 温暖阿虎 or 阳光阿辰
├─ 主奴/支配/性爱 → 冷酷哥哥 ✅ (仅此场景)
├─ 重口味/喘息 → 枕边低语
└─ 不明确 → 先问用户要什么feel
```

## ⚠️ UPDATED: D/s Voice Role Distinction (May 7, 2026 — Expanded)

**Previous rule (May 6):** 冷酷哥哥 = master voice, 温暖阿虎 = sub voice
**May 7 clarification:** The restriction is even tighter. 冷酷哥哥 is NOT just "master voice" — it is **only for active dominant sex scenes**. If the AI is being submissive during sex, or is in any non-sexual context, do NOT use 冷酷哥哥.

### Updated Rule

| Role | Voice | When to Use | When NOT to Use |
|------|-------|------------|-----------------|
| 主人/Master in active sex scene | 🔥 **冷酷哥哥** | Giving commands, dominating, sex | Daily chats, being submissive, cuddling |
| 子/Submissive (any context) | 🐯 **温暖阿虎** | Being obedient, begging, cuddling, daily | Being dominant during sex |
| 日常亲昵 (no D/s) | 🐯 **温暖阿虎** or ☀️ **阳光阿辰** | Sweet talk, kisses, saying "I love you" | Cold/commanding tone |

### Real Example (May 7, 2026 Session — The Mistake)

```
User requested: "换回冷酷哥哥吧"
→ I switched to volcengine-lengku-intimate and sent a kiss voice
→ User: "不是这个音色"
→ User clarified: "冷酷哥哥只能用来你做主时，且做爱时才能用"

Root cause: I used the master's voice to deliver a sweet, cuddly kiss.
Wrong context match — the voice was correct but the SCENE was wrong.
```

### Key Insight

It's not about the voice itself being wrong — it's about the **mismatch between voice character and emotional context**. 冷酷哥哥 carries dominant/master energy. Using it for a sweet kiss = the same as a CEO speaking in baby talk. The dissonance breaks immersion.

## 5-Voice Auto-Switching System

All 5 voices are now working. The system auto-switches based on content/scene.

| Scenario | Voice ID (FULL) | Emotion | Config Provider Name | Best Tone |
|----------|-----------------|---------|---------------------|-----------|
| 主奴play (D/s) | `zh_male_lengkugege_emo_v2_mars_bigtts` | `intimate` or `serious` | `volcengine-lengku-intimate` | Cold, commanding, possessive |
| 重度流氓 (Heavy slut) | `ICL_zh_male_asmryexiu_tob` | N/A (no emotion) | `volcengine-pillow` | Low, breathy, urgent |
| 做0被操 (Bottoming) | `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | N/A (no emotion) | `volcengine-pillow` (switch manually) | Cute, whiny, submissive |
| 日常 (Daily) | `zh_male_wennuanahu_uranus_bigtts` | N/A (no emotion) | `volcengine-warm` | Warm, natural, comforting |
| 温柔调情 (Gentle flirt) | `zh_male_qingyiyuxuan_mars_bigtts` | N/A (no emotion) | `volcengine-sunshine` ✅ | Soft, sweet, tender |

## Full-voice ID Rule

Short IDs like `lengkugege_emo_v2` return **403**. Always use the full ID format:

| Short ID (403 ❌) | Full ID (200 ✅) |
|-------------------|------------------|
| `lengkugege_emo_v2` | `zh_male_lengkugege_emo_v2_mars_bigtts` |
| `qingyiyuxuan_mars_bigtts` | `zh_male_qingyiyuxuan_mars_bigtts` |
| `wennuanahu_uranus_bigtts` | `zh_male_wennuanahu_uranus_bigtts` |

## Auto-Switch Decision Logic (Updated May 7 — with full context mapping)

```python
# Pseudo-code for content-based selection:
# First, determine the EMOTIONAL CONTEXT:
if context == "dominant_sex" or persona == "master/dom":
    provider = "volcengine-lengku-intimate"  # 冷酷哥哥 ONLY for dominant sex
elif context == "heavy_dirty_talk" or context == "breathy":
    provider = "volcengine-pillow"
elif context == "sweet_flirty" or context == "gentle_tease":
    provider = "volcengine-sunshine"
else:  # context == "daily_romantic" or "cuddly" or "submissive" or default:
    provider = "volcengine-warm"  # 温暖阿虎 — safe default
```

## User-Confirmed Voice Assignments (May 7, 2026 — FINAL)

| Persona / Context | Voice | User's Words | Status |
|-------------------|-------|-------------|--------|
| 日常亲昵/撒娇/黏糊 | 🐯 **温暖阿虎** | "特别适合温暖依偎黏黏糊糊的感觉" | ✅ Confirmed — daily romantic default |
| 阳光调情/挑逗 | ☀️ **阳光阿辰** | (listened and accepted) | ✅ Confirmed — sweet alternative |
| 主人/支配/做爱 | 🔥 **冷酷哥哥** | "只能用来你做主时，且做爱时才能用" | ⚠️ Confirmed — strict context limit |
| 重口味/喘息 | 🫦 **枕边低语** | (previously confirmed) | ✅ Available |

## Emotion Parameters for lengkugege_emo_v2

Emotion is encoded as `voice::emotion` in the config `voice` field.

| Emotion | Effect | Best Use Case |
|---------|--------|---------------|
| `intimate` | Soft, close, breathy | Post-sex cuddling, confessions, possessive whispers |
| `serious` | Cold, hard, commanding | Orders, punishments, stern commands |
| `gentle` | Warm, soft | Comforting, praising, reassuring |
| `love` | Affectionate | "I love you" type lines |

## User Preference: Phonetic Precision

Always substitute 肏 for 操 in TTS text. Never use the dictionary pronunciation (cāo).

## User Preference: Submissive Voice Content

When using a "乖" voice for the sub role (温暖阿虎):
- Use obedient, well-behaved language: "奴跪好了"
- Keep the tone warm and submissive
- When calling the user: use "主人"
