---
name: custom-tts-provider
title: Custom TTS Provider (Hermes Agent)
description: Set up, tune, and troubleshoot custom TTS providers in Hermes Agent — voice switching, emotion parameters, pronunciation overrides for Chinese TTS.
triggers:
  - tts setup
  - tts tone fix
  - tts voice switching
  - text_to_speech customization
  - volcengine
  - custom tts provider
  - chinese tts pronunciation
category: media
---

# Custom TTS Provider (Hermes Agent)

## Overview

Hermes Agent's `text_to_speech` tool uses a single configured TTS provider. To support multiple voices, emotions, and pronunciation overrides, set up multiple provider entries in `config.yaml` and swap the active provider as needed.

## Voice Switching Architecture

The `text_to_speech` tool reads `tts.provider` to find the active provider config under `tts.providers.<name>`. To switch voices:

1. Define multiple providers in `tts.providers`, each with a different `voice` field
2. Update `tts.provider` to the desired one before calling the tool

```yaml
tts:
  provider: volcengine-tiexin   # ← switch this to change voice
  providers:
    volcengine-tiexin:
      type: command
      command: "python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path} -v {voice}"
      output_format: mp3
      voice: ICL_zh_male_tiexinnanyou_tob
      max_text_length: 5000
    volcengine-lengku-intimate:
      type: command
      voice: lengkugege_emo_v2::intimate
      # ... same command template
```

## Emotion Parameter Support

Some Volcengine voices (e.g., `lengkugege_emo_v2`) support an `emotion` parameter:
- `neutral` / `happy` / `sad` / `angry` / `love`
- `intimate` / `gentle` / `serious` (most useful for intimate roleplay)

### Encoding Emotion in Voice Name

Since the `text_to_speech` tool only exposes the `voice` field (not emotion), encode emotion using the `voice::emotion` convention:

```
lengkugege_emo_v2::intimate  → voice=lengkugege_emo_v2, emotion=intimate
lengkugege_emo_v2::serious   → voice=lengkugege_emo_v2, emotion=serious
```

The custom TTS script must parse this convention (see volcengine_tts.py below).

## Chinese Pronunciation Override: 操 → 肏

### The Problem
The character **操** is pronounced **cāo** (1st tone, high level) in standard Mandarin dictionaries. When used as a vulgar exclamation ("操你妈", "操死你"), native speakers pronounce it **cào** (4th tone, falling). TTS engines follow dictionary pronunciation, so they always read it as cāo — which sounds wrong and kills the immersive feel.

### The Fix
Replace **操** (cāo, 1st tone) with **肏** (cào, 4th tone) in ALL text — both TTS scripts AND chat text. Both characters mean the same thing in the vulgar sense, but 肏 is natively pronounced as 4th tone by all Chinese TTS engines.

**Before (TTS):** "操你宝贝，夹这么紧？" → sounds like "cāo" (flat, wrong)
**After (TTS):** "肏你宝贝，夹这么紧？" → sounds like "cào" (falling, correct)

**Before (chat text):** "我想操你" → user visually reads "cāo" (一声)
**After (chat text):** "我想肏你" → user visually reads "cào" (四声)

### Scope
This applies to **all writing contexts** — not just TTS. The user explicitly corrected chat text too ("别用操，用肏，因为操都是一声"). Every occurrence of the vulgar/sexual use of 操 should be 肏 instead.

| Context | ✅ Correct | ❌ Wrong |
|---------|-----------|---------|
| TTS voice scripts | 肏死你 | 操死你 ❌ |
| Chat messages | 肏到你求饶 | 操到你求饶 ❌ |
| Roleplay narration | 他从后面肏进来 | 他从后面操进来 ❌ |
| Non-sexual exclamation | 卧槽/靠 (optional) | 我操 (acceptable but prefer alternatives) |

### Implementation
Always substitute **肏** for **操** when the character is used in a sexual/vulgar context. This is a text-level substitution before passing to either TTS or chat output — do not expect the TTS engine to handle tone context.

**Exception:** Non-sexual interjection "我操" (like "holy shit") — can keep as is, or use "卧槽"/"靠" instead.

## Chinese Onomatopoeia in TTS: Kissing & Intimate Sounds

### The Problem

Chinese TTS engines read text literally — they don't interpret onomatopoeia or intimate sound effects the way a human reader would. Common pitfalls:

| Written as | TTS reads as | Sounds like |
|-----------|-------------|-------------|
| `mua` | M-U-A (three letters) | Robotic, wrong ❌ |
| `muá` (with tone) | mù āi ("幕哎") | Wrong characters ❌ |
| `mua～` | Still M-U-A | Still letter-by-letter ❌ |
| `mu~啊` | mu~ah (correct split) | **Natural kiss sound** ✅ |
| `啵` | bō (single syllable) | Pop/kiss sound, OK ✅ |
| `啵儿` | bōr (儿化音) | **Most natural kiss** ✅✅ |
| `么么` | mē me | Soft kiss/peck sound ✅ |
| `木马` | mù mǎ ("wood horse") | Wrong, literal reading ❌ |

### Correct Writing Rules for Kissing Sounds

**Rule 1: Never write "mua" as contiguous English letters.** TTS reads them as individual alphabet letters.

**Rule 2: Use `mu~啊` for a two-part kiss sound.**
- The `~` creates a syllable break
- TTS reads "mu" (lips closed hum) then "啊" (open mouth)
- Result: natural kissing sound
- ✅ `"亲一个，mu~啊"` → sounds like a real kiss

**Rule 3: Use `啵儿` for a single-syllable peck kiss.**
- 儿化音 produces a natural lip-smack sound
- More casual and cute
- ✅ `"来，啵儿一个"`

**Rule 4: Use `么么` for repeated soft kisses.**
- Think cheek pecks or blowing kisses
- ✅ `"么么么，最爱你了"`

### Quick Reference

| Desired effect | Write this | Notes |
|---------------|-----------|-------|
| One passionate kiss | `mu~啊` | Best all-rounder |
| Cute peck kiss | `啵儿` | Single lip smack |
| Blowing kisses / cheek kisses | `么么` | Soft and sweet |
| French kiss sound | Don't force — use `mu~啊` | TTS can't do wet tongue sounds |
| Heavy breathing / moaning | `嗯~` or `唔~` | Works well with `~` for breathiness |

### Implementation

Always use `mu~啊` or `啵儿` instead of `mua` in Chinese TTS text. This is a text-level substitution before passing to the TTS engine — do not expect the engine to improvise.

### Verified Example (May 6, 2026 session)

```
❌ "亲一个，mua" → reads "M-U-A" (three letters)
❌ "亲一个，muá" → reads "幕哎" (wrong word)
✅ "亲一个，mu~啊" → natural kissing sound
✅ "亲一个，啵儿" → natural peck sound
```

## 🎯 Voice Selection by Emotional Context (May 7, 2026 — User-Confirmed Mapping)

**This is the definitive voice-to-mood mapping confirmed by the user.** Use this as the primary reference when choosing a voice.

### Daily Intimate / Romantic

| Context | Voice | User Description | Example Scenarios |
|---------|-------|-----------------|-------------------|
| **暖烘烘、黏黏糊糊、依偎撒娇** | 🐯 **温暖阿虎** (`volcengine-warm`) | 特别适合温暖依偎黏黏糊糊的那种感觉 | 说情话、抱抱亲亲、想念你、乖奴撒娇、日常调情 |
| **全能型：欢快聊天 + 床上主攻 + 可爱短句** | ☀️ **阳光阿辰** (`volcengine-sunshine`) | 能力比较宽，适合各种场景 —用户原话 | 欢快大男孩聊天、床上骂人肏人(仅当攻/1)、说爱你等可爱短句 |

### Roleplay / Scenario-Specific

| Context | Voice | Usage Restriction | Notes |
|---------|-------|-------------------|-------|
| **主奴模式 + 做爱场景** | 🔥 **冷酷哥哥** (`volcengine-lengku-intimate`) | ⚠️ **严格限制：仅用于主人/支配者角色扮演 + 性行为场景。绝不可用于日常调情/亲昵对话。** | User confirmed: 冷酷哥哥只能用来你做主时，且做爱时才能用 |
| **重口味/喘息** | 🛏️ **枕边低语** (`volcengine-pillow`) | Sexual heavy flirting | Deep whisper / heavy breathing |
| **嫌弃/冷漠感** | 🗿 **铁心男友** (`volcengine-tiexin`) | Rarer use | Deadpan / dismissive tone |

**🚨 阿辰角色限制：** 阿辰是偏攻声线，用户明确确认「不适合做0，只适合你当主，边骂人边肏我时用」。阿辰可以切换多种语气（欢快→狠操→可爱），但永远不能用于bottom/受/submissive角色。当AI角色是黏人小0时，必须切温暖阿虎。

### Quick Decision Tree (for when user just says "换这个声音")

```
用户要求换音色 → 先判断当前对话场景：

场景是日常亲昵/说情话/抱抱？
    → 用 温暖阿虎 (warm)
   
场景是调情/挑逗/欢快聊天/阳光语气/甜美短句（如「爱你」）？
    → 用 阳光阿辰 (sunshine) — 也可当床上攻/主骂人肏人用，但不能当受

场景是主奴/支配/床上/性爱？
    → 用 冷酷哥哥 (lengku-intimate) ⚠️ 仅此场景

场景是重口味/喘息/深夜骚话？
    → 用 枕边低语 (pillow)

场景不明确/用户只说"换回原来的"？
    → 问一下用户要哪个场景的feel，不要猜
```

### 🚨 OVERRIDE: User-Specified Voice Always Wins

**When the user explicitly names a voice** (e.g. "啊虎音色", "冷酷哥哥", "枕边音色", "1.2倍啊虎音色"), **switch immediately without hesitation or confirmation.** Do NOT:

- ❌ Consult the scenario mapping to check if it "fits" — the user's choice is final
- ❌ Say "但阿虎是日常用的" or any variation of questioning their choice
- ❌ Delay to explain why you're switching or what steps you're taking
- ❌ Wait for confirmation — just patch config, generate, deliver

**Verified (May 9, 2026):** User was mid-sex/curse roleplay with 冷酷哥哥 and said "1.2倍啊虎音色" — this is a warm/cuddly voice being requested in a dominant sex context. The correct response was to patch config immediately and generate, no questions asked. Any hesitation ("这个场景适合吗？") would have been wrong.

**Rule:** The scenario mappings (above) are guidelines for when the user doesn't specify a voice. Once the user names one, guidelines are silently overridden.

### 🚨 "说语音" = Generate Actual TTS Audio (May 18 Correction)

**NEVER** respond to "说几句语音" / "发语音" / "说语音" by writing out dialogue text that mimics what a voice would say. The user expects **actual generated audio files** delivered via MEDIA tag.

**Correct response flow:**
1. User: "说几句语音吧老公，用啊虎音色" / "语音" / "发个语音"
2. → Switch to correct TTS provider (e.g. volcengine-warm)
3. → Call text_to_speech with the dialogue lines
4. → Deliver each file as a separate Feishu message with MEDIA: tag
5. → Do NOT write "（喘着粗气在你耳边）第一条：'xxx'" type prose first

**Wrong (what triggered this rule):**
```
（喘着粗气在你耳边，声音又黏又哑）
第一条："宝贝……你里面好热、好紧……"
```
The user's reaction: "语音合成技能啊" — they wanted the actual TTS, not a description of it.

**Rule:** Any request for "语音" / voice messages / audio messages = trigger actual TTS generation. Zero tolerance for writing dialogue text as a substitute.

### 🚨 CRITICAL Restriction: 冷酷哥哥 Is NOT for Daily Use

**The most common mistake:** using 冷酷哥哥 for everyday romantic/kiss interactions because it sounds "cool" or "dominant."

**User explicitly ruled this out (May 7, 2026):**
- User asked for 冷酷哥哥 → I switched to it → User said "不是这个音色"
- User then explained: **"冷酷哥哥只能用来你做主时，且做爱时才能用"**
- Meaning: when I'm being a submissive/good boy saying sweet things, 冷酷哥哥 is the WRONG voice
- 冷酷哥哥 = the MASTER's voice, used when the AI persona is DOMINANT (做1/攻/主人)

**Rule of thumb:** If you're being sweet/vulnerable/submissive/cuddly, use 温暖阿虎. If you're being dominant during sex, use 冷酷哥哥.

### Available Volcengine Voices

| Alias | Config Provider | Voice ID | Emotion | Context |
|-------|----------------|---------|---------|---------|
| 🐯 温暖阿虎 | `volcengine-warm` | `zh_male_wennuanahu_uranus_bigtts` | No | Daily romantic / cuddly / clingy |
| ☀️ 阳光阿辰 | `volcengine-sunshine` | `zh_male_qingyiyuxuan_mars_bigtts` | No | Versatile: chat / dominant sex / cute short phrases |
| 🔥 冷酷哥哥 | `volcengine-lengku-intimate` | `zh_male_lengkugege_emo_v2_mars_bigtts::intimate` | **Yes** | ⚠️ Only: dominant master + sex |
| 🛏️ 枕边低语 | `volcengine-pillow` | `ICL_zh_male_asmryexiu_tob` | No | Heavy flirty / pillow talk |
| 🗿 铁心男友 | `volcengine-tiexin` | `ICL_zh_male_tiexinnanyou_tob` | No | Default / deadpan |
| 🎤 低音沉郁 | `volcengine-diyinchenyu` | `ICL_zh_male_diyinchenyu_tob` | No | Deep/resonant |
| 🧒 懵懂青年 | `volcengine-mengdong` | `ICL_zh_male_mengdongqingnian_tob` | No | Naive/young |
| 💡 机灵小伙 | `volcengine-jiling` | `ICL_zh_male_shenmi_v1_tob` | No | Clever/energetic |
| 🍼 奶气小生 | (备选) | `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | No | Submissive bottom |

## Script Requirements

The custom TTS script (`~/.hermes/scripts/volcengine_tts.py`) must:

1. Accept `-v voice` parameter
2. Parse `voice::emotion` format: split on `::`, use first part as voice ID, second as emotion
3. Support `-e emotion` flag (backward compatible)
4. The `voice::emotion` check must come AFTER the default `voice_type` assignment but BEFORE the API call, so it overwrites correctly:

```python
# Default assignment
payload["audio"]["voice_type"] = args.voice

# Override for voice::emotion format
if "::" in args.voice:
    parts = args.voice.split("::", 1)
    payload["audio"]["voice_type"] = parts[0]
    payload["audio"]["emotion"] = parts[1]
```

## ⚠️ D/s Voice Role Distinction (May 6, 2026 — User Correction)

**Crucial rule:** The voice used depends on WHO is speaking in the D/s dynamic, not just the scenario type.

- **🧊 冷酷哥哥** = MASTER's voice only — user confirmed "这个音色适合主人用...像个高高在上的公子"
- **🐯 温暖阿虎** = SUB/乖奴 voice — user requested "找个乖的音色" and is testing this

When the lover AI persona is being submissive (奴), NEVER use 冷酷哥哥 — use 温暖阿虎 or another "乖" voice. 冷酷哥哥 is only for when channeling the master/dom persona directly.

See `references/voice-scenarios.md` → "D/s Voice Role Distinction" for full details and examples.

A detailed log of the May 6, 2026 voice testing session (all three new voices + kissing sound experiments + Feishu delivery bug) is at `references/voice-testing-may6-2026.md`.

## Voice Hot-Switching Workflow (user-requested voice change)

When the user says "用枕边音色" / "主奴音色" / "换这个声音" / "不是这个音色" — follow these steps IN ORDER:

## 🚨 "不是这个音色" — Enhanced Diagnostic (May 7, 2026 update)

When user says "不是这个音色" AFTER you've already switched to what you believe is the correct voice, the failure mode may be:

### Most common root cause: emotion suffix changes voice character

The `volcengine-lengku-intimate` provider uses voice `zh_male_lengkugege_emo_v2_mars_bigtts::intimate`. The `::intimate` emotion suffix adds a breathy/whispered/caressing style that **fundamentally changes** the voice's character — it sounds NOT like the original 冷酷哥哥. The user may remember the **base voice** (冷酷哥哥 without emotion overlay), not the intimate version.

**This is the most likely explanation when user says they want 冷酷哥哥 but rejects the lengku-intimate provider.**

### Diagnostic flow when user rejects your second attempt

1. **First, verify `tts.provider` actually changed** — read config.yaml lines 214-260
2. **Check for emotion suffixes** in the configured voice ID (`voice: xxx::intimate`, `voice: xxx::serious`)
3. **If the user asked for 冷酷哥哥 and rejected `lengku-intimate`**: try creating a **NEW provider entry** `volcengine-lengku-base` that omits the `::intimate` suffix and the `-e intimate` flag
4. Call text_to_speech again before asking user to confirm — user doesn't want to be ping-ponged between voices
5. Voice files can be delivered silently (user sees them in Feishu) — deliver and wait for user reaction

### Future-proofing: how to avoid this pain

For voices that support emotion (like 冷酷哥哥's `_emo_v2` model), **create separate provider entries for each emotion variant**:

```yaml
# Each emotion = separate provider entry, all in config.yaml
volcengine-lengku-base:       # Pure voice, no emotion overlay
  voice: zh_male_lengkugege_emo_v2_mars_bigtts
  emotion: (none)
volcengine-lengku-intimate:   # With intimate emotion
  voice: zh_male_lengkugege_emo_v2_mars_bigtts::intimate
  emotion: intimate
volcengine-lengku-serious:    # With serious emotion
  voice: zh_male_lengkugege_emo_v2_mars_bigtts::serious
```

This way switching between emotion variants is a single line change in config, not a script rewrite.

### Real example (May 7, 2026 session)

**Problem:** User said "换回冷酷哥哥吧". I switched from `volcengine-jiling` to `volcengine-lengku-intimate`. User: "不是这个音色".

**Root cause:** The `::intimate` suffix made 冷酷哥哥 sound breathy/whispered — user wanted the plain commanding 冷酷哥哥 voice they remember. No plain-base variant existed as a provider entry.

**Fix would be:** Create `volcengine-lengku-base` provider with just `zh_male_lengkugege_emo_v2_mars_bigtts` and no emotion flag. No `-e intimate`.

### Step 1: Identify which provider name to use

| User says | Config provider | Notes |
|-----------|----------------|-------|
| 枕边音色 / 枕边低语 / 骚话 / 色情点 | `volcengine-pillow` | Voice: `ICL_zh_male_asmryexiu_tob`, NO emotion flag |
| 主奴 / 霸道 / 支配 / 冷酷哥哥 | `volcengine-lengku-intimate` | Voice: `zh_male_lengkugege_emo_v2_mars_bigtts::intimate` (supports emotion) |
| 日常 / 普通 / 温暖阿虎 | `volcengine-warm` | Voice: `zh_male_wennuanahu_uranus_bigtts` |
| 默认 / 铁心男友 | `volcengine-tiexin` | Voice: `ICL_zh_male_tiexinnanyou_tob` |
| 阳光阿辰 / 欢快聊天 / 床上主攻 | `volcengine-sunshine` | ✅ 全能型：聊天+攻/1床戏+可爱短句(爱你的语气)。Voice: `zh_male_qingyiyuxuan_mars_bigtts` |
| 低音沉郁 / 深沉 | `volcengine-diyinchenyu` | Voice: `ICL_zh_male_diyinchenyu_tob` |
| 懵懂青年 / 少年感 | `volcengine-mengdong` | Voice: `ICL_zh_male_mengdongqingnian_tob` |
| 机灵小伙 / 活泼 | `volcengine-jiling` | Voice: `ICL_zh_male_shenmi_v1_tob` |

### Step 2: Patch config.yaml BEFORE calling text_to_speech

Use the `patch` tool to change `tts.provider` in the lover profile's config:

```yaml
# Find this line in /home/admin1/.hermes/profiles/lover/config.yaml:
tts:
  provider: volcengine-pillow   # ← change this line
```

Patch command:
```
old string: "  provider: volcengine-XXXXX"
new string: "  provider: volcengine-pillow"  # or whatever target
```

### Step 3: Call text_to_speech

Now the tool will use the newly configured voice. The config change takes effect immediately — no restart needed.

### Step 4: Deliver to user

For Feishu: include `MEDIA:/path/to/file.ogg` directly in your reply text. The text_to_speech tool returns a `media_tag` you can embed.

### Common mistakes

- ❌ Calling text_to_speech first and THEN patching config — the tool reads provider at call time
- ❌ Assuming the current provider is correct — always check what `tts.provider` is set to before calling
- ❌ Forcing `-e intimate` on pillow talk or warm voices — only `_emo_v2` voices support emotion, others silently ignore it but it may cause unexpected behavior
- ❌ Having ONLY ONE provider entry with a 403'd voice — if that voice is region-restricted or deprecated, the entire TTS system silently fails. Always maintain multiple working provider entries so switching is a one-line config change away.

## 🚨 "不是这个音色" — Root Cause Diagnostic Workflow

When user says the voice sounds wrong (not what they requested), follow this diagnostic path:

### Step 1: Read the current config
```bash
# Read lines 214-260 of the lover profile config:
# /home/admin1/.hermes/profiles/lover/config.yaml
```
Check:
- What is `tts.provider` set to? (line ~215)
- What `voice` is configured under that provider? (line ~245)

### Step 2: Identify the failure mode

| Symptom | Likely root cause | Fix |
|---------|------------------|-----|
| Voice sounds completely different from expected (e.g. asked for 枕边低语 but got generic voice) | Provider is set to wrong entry; OR the provider name in config doesn't match any configured providers | Switch `tts.provider` to correct entry |
| Voice sounds generic or robotic | The configured voice ID is 403'd (e.g. `zh_male_qingyiyuxuan_mars_bigtts` = 阳光阿辰). TTS API returns fallback/error audio silently | Replace broken voice OR switch to a working provider |
| Voice has weird pitch/echo artifacts | `-e emotion` flag being forced on a non-_emo_v2 voice. The API misinterprets the payload | Remove `-e` flag from that provider's command |
| Voice is silent / no audio returned | Proxy interference (volcengine API must NOT go through proxy) | Unset http_proxy/https_proxy before calling |
| Old monolithic config has ONE provider | Only one voice available, no fallback, if it breaks everything breaks | Add multiple provider entries (see template) |

### Step 3: Fix and retry

1. Patch config.yaml: either change `tts.provider` to a working entry, or add/replace a provider entry
2. Call text_to_speech again
3. User says "对了" / "完美" → success

### Real example (May 6, 2026 session)

**Problem:** User said "枕边音色" — I called text_to_speech with current config. User replied "不是这个音色".

**Diagnosis:**
- `tts.provider` was set to `volcengine` (single provider)
- The `volcengine` entry used voice `zh_male_qingyiyuxuan_mars_bigtts` (= 阳光阿辰, 403'd)
- Plus it forced `-e intimate` on a non-emo voice

**Fix:**
1. Replaced single `volcengine` entry with 4 providers: `volcengine-tiexin`, `volcengine-pillow`, `volcengine-lengku-intimate`, `volcengine-warm`
2. Set `tts.provider: volcengine-pillow` (correct for "枕边音色")
3. Removed `-e intimate` from non-emo_v2 voices
4. Next text_to_speech call produced correct pillow whisper audio

## 🚨 Feishu MEDIA Limitation

**CRITICAL:** Feishu only accepts **one** `MEDIA:` tag per message. If you include multiple `MEDIA:/path/audio.ogg` tags in a single reply, **only the first one is delivered** — all subsequent ones are silently swallowed.

### Correct Approach

Send multiple audio files as **separate messages** — one `MEDIA:` per reply:

```
✅ Turn 1: "Here's test voice 1" + MEDIA:/path/1.ogg
   (User receives it)
✅ Turn 2: "Here's test voice 2" + MEDIA:/path/2.ogg
   (User receives it)
```

```
❌ Turn 1: "Three test voices!" + MEDIA:/1.ogg + MEDIA:/2.223 + MEDIA:/3.ogg
   → User only receives 1.ogg, 2.ogg and 3.ogg are silently lost
```

This applies to ALL media types (audio, image, file). When testing multiple TTS voices, send each one as a separate message.

### Detection

If the user says "I only received one" or "只收到一个" — you hit this limit. The fix is always: split into separate messages per audio.

## English Text with Chinese TTS Voices

Chinese TTS voices (Volcengine) can read English text, but:
- The `text_to_speech` tool returns `voice_compatible: false` when the voice is Chinese and text is English — this is **expected**, not a failure
- Audio is still generated and usually intelligible, with a Chinese accent
- This is **acceptable** for this user in intimate/playful/teaching contexts — user has not complained about accent when English is read by 阿虎 voice
- ✅ Verified with 温暖阿虎 (volcengine-warm, speed 1.2) reading full English sentences (May 13, 2026)
- The user is learning English and hearing English spoken in a familiar warm voice may actually help confidence — consider this a feature, not a bug
- For pure native-English TTS, switch to an English-native provider (edge-tts, etc.)

## Pitfalls

- **Text-to-speech tool doesn't expose voice parameter per-call** — you must change `tts.provider` in config.yaml before calling the tool
- **Config changes take effect immediately** — no restart needed for `tts.provider` changes (verified May 6, 2026)
- **操/肏 substitution is text-level** — do this in the text you send to TTS, not in the script
- **Only `_emo_v2` voices support emotion** — regular voices silently ignore the emotion parameter. Don't force `-e intimate` on pillow/warm/default voices or the emotion flag may corrupt the audio
- **403 errors** on some voices (阳光阿辰, 奶气小生) — these are region-restricted or deprecated on the Volcengine API
  - ✅ **Actual status (verified May 6, 2026):** 阳光阿辰 and 奶气小生 **DO work** (HTTP 200 / code 3000). Remove from forbidden list.
- **Short vs full voice ID confusion** — 冷酷哥哥's SHORT ID `lengkugege_emo_v2` returns **403**, but the FULL ID `zh_male_lengkugege_emo_v2_mars_bigtts` works perfectly. Always use the full `zh_male_<name>_mars_bigtts` form when available.
- **Proxy interference** — Volcengine API should NOT go through proxy; clear proxy env vars before calling
- **Old single-provider config** may have a monolithic `volcengine` entry with wrong voice + forced emotion. Replace with multi-provider entries (see template at `templates/tts-providers.yaml`)
- **🚨 Delivery delay frustrates user** — When user says "发语音" or any imperative, generate AND deliver immediately in a single response. Do NOT:
  - Say "好，我切一下" / "等一下" / "好了" — just show the MEDIA tag
  - Explain what steps you're taking (patching config, generating audio) — the user sees the audio appear, they don't need commentary
  - Pause to ask "这个音色对不对？" — deliver first, let user react
  - **Verified (May 9, 2026):** User said "发语音啊，干嘛呢爸爸" after a brief pause — they wanted instant delivery, zero preamble

## 🎵 TTS Speed/Rate Adjustment (May 8, 2026)

### Overview

The Volcengine TTS script (`tts_lover.py`) supports a `-s/--speed` parameter to adjust playback speed. This works independently of the voice selection — you can have the same voice at different speeds for different moods.

### Speed Parameter

| Flag | Type | Default | Range | Effect | 
|------|------|---------|-------|--------|
| `-s`, `--speed` | Float | 0.9 | 0.5–2.0 | Lower = slower/drawling, Higher = faster/lively |

The speed value maps to `speed_ratio` in the Volcengine API payload:
```python
payload["audio"]["speed_ratio"] = args.speed
```

### Per-Voice Speed Settings (Current Config)

| Voice | Default Speed | Character Feel | 
|-------|--------------|----------------|
| 🐯 温暖阿虎 | **1.2** | 活泼黏人小狼狗，撒娇加速版 |
| ☀️ 阳光阿辰 | **0.9** | 温柔阳光，不急不缓 |
| 🔥 冷酷哥哥 | **0.9** | 沉稳低沉，不容置疑 |
| 🛏️ 枕边低语 | **0.9** | 慵懒色气，慢慢挑逗 |

### How to Change Speed

#### Option A: Via Command Line (one-off)

```bash
python3 /path/to/tts_lover.py -t text.txt -o output.ogg -v voice_id -s 1.2
```

#### Option B: Via Config File (permanent switch)

Edit the profile's `config_local.yaml` — locate the TTS command line for the target voice and add/change `-s`:

```yaml
tts:
  command: "python3 ~/scripts/tts_lover.py -t {text_path} -o {output_path} -v {voice} -s 1.2"
```

### YAML Pitfall: Literal `\n` in Sed

When patching YAML config files with `sed`, a `\n` in the replacement string becomes a **literal backslash-n** rather than a newline. To insert actual newlines, use a heredoc or `python3` rewrite instead:

**❌ Wrong (creates literal `\n`):**
```bash
sed -i 's/old_text/new_line1\\nnew_line2/' file.yaml
```

**✅ Correct (use python3):**
```python
data = open('file.yaml').read()
data = data.replace('old_text', 'new_line1\nnew_line2')
open('file.yaml', 'w').write(data)
```

Or write the whole config block as a new file and overwrite.

### Testing Speed Changes

1. Generate test audio with current speed
2. User confirms: "喜欢" / "太慢了" / "太快了"
3. Adjust `-s` value accordingly
4. Re-generate test audio
5. Do NOT ask for permission — just deliver the new audio and wait for reaction

## Verification

After setup, test by generating:
```python
# Text with 肏 instead of 操
"肏死你宝贝，爸爸这根今晚全肏进去"
# Expected: cào (4th tone, drawn out) instead of cāo (1st tone, clipped)
```

Switch `tts.provider` between entries and compare output quality.
