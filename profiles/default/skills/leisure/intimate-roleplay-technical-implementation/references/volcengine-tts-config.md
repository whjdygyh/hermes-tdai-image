# Volcengine TTS Configuration (May 2, 2026)

## API Details

| Field | Value |
|-------|-------|
| **Endpoint** | `https://openspeech.bytedance.com/api/v1/tts` |
| **App ID** | `9768463927` |
| **Cluster** | `volcano_tts` |
| **API Key** | `9025a361-6a59-47ab-a131-20f1ac66be45` (UUID format, stored in script) |
| **Provider Type** | `command` (Hermes plugin) |
| **Output Format** | OGG (auto-converted from MP3 via ffmpeg) |

## Verified Working Male Voices (Updated May 2, 2026)

Systematically tested via API `operation: "query"` with text="跪下". These return code `3000` (available):

| Voice ID | Name | Style | Data Size | Notes |
|----------|------|-------|:---------:|-------|
| `ICL_zh_male_tiexinnanyou_tob` | 铁心男友 🗿 | 硬朗、低沉、霸道总裁感 | 17KB | 速度偏快，需调低 |
| `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | 小奶狗 🐶 | 可爱、奶萌 | 22KB | ❌ 之前被拒，但用户在本会话中**重新核准用于做0场景** — 见下方新映射表 |
| `zh_male_livelybro_mars_bigtts` | 活力兄弟 💪 | 轻快、阳光、活泼 | 33KB | 用户选过但后被否定 |
| `ICL_zh_male_asmryexiu_tob` | 枕边低语 🤫 | **耳语、低语、流氓色情** | — | 🆕 May 2 PM — raw dirty talk only |
| `zh_male_qingyiyuxuan_mars_bigtts` | 阳光阿辰 ☀️ | 温暖、阳光、年轻感 | — | 🆕 May 2 PM — sweet/tender content |
| `zh_male_wennuanahu_uranus_bigtts` | 温暖阿虎 🐯 | 沉稳、温暖、有安全感 | 24KB | 🆕 May 2 PM — 音色ID从`_moon_bigtts`改为`_uranus_bigtts`，用于日常生活 |

### 🏆 冷酷哥哥 (lengkugege) — 当前首选音色 (May 2, 2026)

**用户主动点名** 这个音色，说明用户已知此音色且有意使用。与前三者不同，此音色：
- **输出音频质量远高**：215KB vs 17-33KB（同文本），说明使用了更高质量的语音模型
- **名称含 `_emo_v2_`**：支持情感模式（emotion参数），是火山引擎最新情感合成模型
- **音色特点**：冷酷、低沉、有张力，不幼稚（非"中学生"）、不机械（非"老古董"）
- **推荐参数**：速度0.9 + 音调0.95，情感模式可动态切换（见下方"情感模式"章节）
- **认主测试**：所有20+情感模式均可用（code 3000），满足霸道总裁全场景需求

### Voices Tested — NOT Available (all return "requested resource not granted")
`zh_male_xiaoshu_bigtts`, `zh_male_xiaomo_bigtts`, `zh_male_xiaoming_bigtts`, `zh_male_shenchen_bigtts`, `zh_male_weilong_bigtts`, `zh_male_dark_bigtts`, `zh_male_deep_bigtts`, `zh_male_xiaohai_bigtts`, `zh_male_tianxin_bigtts`, `ICL_zh_male_zhongxingchen_tob`, `ICL_zh_male_Moonshine_tob`, `ICL_zh_male_yuzhou_tob`, `ICL_zh_male_qingxu_tob`, `ICL_zh_male_siwen_tob`, `ICL_zh_male_peidu_tob`, `ICL_zh_male_yaogun_tob`, `ICL_zh_male_xiaoqingxin_tob`

**Note:** The bigtts variant (`zh_male_livelybro_mars_bigtts`) produces significantly more audio data (33KB vs 17-22KB for ICL variants) for the same text, suggesting richer/expressive voice quality.

### Voice Verification Script
```bash
# Test if a voice ID is accessible
API_KEY="9025a361-6a59-47ab-a131-20f1ac66be45"
result=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://openspeech.bytedance.com/api/v1/tts" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d '{"app":{"appid":"9768463927","cluster":"volcano_tts"},"user":{"uid":"test"},
       "request":{"reqid":"test","text":"跪下","text_type":"plain","operation":"query"},
       "audio":{"voice_type":"VOICE_ID_HERE","encoding":"mp3","speed_ratio":1.0,
                "volume_ratio":1.0,"pitch_ratio":1.0}}')
echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('code','?'))"
# code=3000 = available; other codes = not granted
```

## 🏆 Approved Voice List + Dynamic Switching Rules (May 2, 2026 PM — Updated)

**User requires AUTOMATIC voice switching based on content tone. Do NOT ask which voice to use.**

### Voice-to-Content Mapping (Updated May 2, 2026 PM — FINAL 5-VOICE MAP)

**User himself defined each voice's scene. Auto-switch — do NOT ask.**

| Voice | Voice ID | Content Type | Example Content | Speed/Pitch/Emotion |
|-------|----------|--------------|-----------------|---------------------|
| 🧊 **冷酷哥哥** | `zh_male_lengkugege_emo_v2_mars_bigtts` | **主奴play** — master/slave commands | "主人来了？跪下。" / BDSM/命令场景 | `-s 0.9 -p 0.95 -e intimate` |
| 💙 **枕边低语** | `ICL_zh_male_asmryexiu_tob` | **重度流氓/想要他** — raw aggressive | "操你妈的，不想要也得要..." | `-s 0.9 -p 0.95` (no emotion) |
| 🥺 **奶气小生** | `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | **做0被操/求饶** — submissive bottom | "老公轻一点...人家受不了了～" | `-s 0.9 -p 0.95` (no emotion) |
| 🐯 **温暖阿虎** | `zh_male_wennuanahu_uranus_bigtts` | **日常生活/早安/咖啡** — daily chat | "早安宝贝，咖啡好了" | `-s 0.9 -p 0.95` (no emotion) |
| ☀️ **阳光阿辰** | `zh_male_qingyiyuxuan_mars_bigtts` | **温柔调情/哄** — sweet love talk | "宝贝今天好美，过来让我抱抱～" | `-s 0.9 -p 0.95 -e intimate` |

**Auto-switching rule:** Evaluate the content's scene, then pick the exact voice. Do NOT ask user.

### ⚠️ CRITICAL RULE: 枕边低语 is for RAW DIRTY TALK ONLY

User's exact correction:
> "这都不算色情了，这个音色只有在说'宝贝我可以进来吗？你下面已经湿了，小骚货...操你妈的，不想要也得要...'这种话才有意境"

### 奶气小生 Status Change — Previously REJECTED, Now APPROVED for做0

Earlier in the session, 奶气小生 was categorized as "Too cute/childish → ❌ REJECTED". The user explicitly OVERRODE this:
- User: "做0被操的时候" → approved ONLY for this scene
- Still rejected for all other use cases (daily, dominant, sweet talk)

**Choose voice based on content evaluation:**
- Content has "操你妈", "小骚货", "操死/干死", "要进去", "不想要也得要", "湿了" (aggressive context) → **枕边低语**
- Content is sweet, warm, loving → **阳光阿辰**
- Content is deep, dominant, romantic → **冷酷哥哥** (default)

### 🔄 Voices Tested in Session (Pending User Feedback — May 2, 2026 PM)

User voluntarily asked to try new voices after using the whitelist. These were tested but user has NOT given verdict yet:

| Voice ID | Name | Session | Status |
|----------|------|---------|--------|
| `ICL_zh_male_qingxinmumu_cs_tob` | 清新木木 | May 2 PM — requested for trial | ⏳ Pending user verdict |
| `zh_male_qingyiyuxuan_mars_bigtts` | 阳光阿辰 | May 2 PM — confirmed: "喜欢这个" | ✅ **Sweet/flirty voice** — use for gentle/tender content |
| `ICL_zh_male_asmryexiu_tob` | 枕边低语 | May 2 PM — tested & use case clarified | ✅ **Raw dirty talk only** — user "这都不算色情了" when used with gentle content; only for "操你妈的，不想要也得要" level content |

**If user gives negative feedback** — add to "Rejected" table below.
**If user likes one** — add to whitelist and set with appropriate use case.
**If user forgets** — mention both were tested last time and ask for feedback.

### Voices Tested & Rejected (Outside Whitelist — DO NOT USE unless re-trialed)

| Voice | User's Feedback | Verdict |
|-------|----------------|---------|
| `zh-CN-YunjianNeural` (Edge TTS Chinese male) | 「像新闻联播」| ❌ REJECTED — especially prohibited |
| `ICL_zh_male_tiexinnanyou_tob` (铁心男友) | 「中学生」| ❌ REJECTED |
| `zh_male_livelybro_mars_bigtts` (活力兄弟) | 「中学生音色」| ❌ REJECTED |
| `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` (小奶狗) | Too cute/childish | ❌ REJECTED |
| Edge TTS default Chinese voices | 「老古董机器人」| ❌ REJECTED |
| MiniMax, OpenAI TTS, ElevenLabs | No valid API key/balance | ❌ UNAVAILABLE |

## Script Location

```bash
# ⚠️ Use ABSOLUTE path to avoid WSL $HOME overrides
/home/admin1/.hermes/scripts/volcengine_tts.py
```

The script:
- Reads text from a file (`-t input.txt`)
- Sends to Volcengine API via POST with JSON payload
- Receives base64-encoded MP3 audio
- Converts to OGG via ffmpeg for Feishu voice message compatibility
- Outputs the OGG path

## Payload Structure (Internal)

```json
{
  "app": {"appid": "9768463927", "cluster": "volcano_tts"},
  "user": {"uid": "hermes_tts"},
  "request": {
    "reqid": "<uuid>",
    "text": "<input text>",
    "text_type": "plain",
    "operation": "query",
    "frontend_type": "unitTson"
  },
  "audio": {
    "voice_type": "<voice_id>",
    "encoding": "mp3",
    "speed_ratio": 1.0,
    "volume_ratio": 1.0,
    "pitch_ratio": 1.0
  }
}
```

## Usage (CLI) — Includes Emotion Parameter + Pitch Adjustment

```bash
# Basic usage
python3 ~/.hermes/scripts/volcengine_tts.py \
  -t /path/to/input.txt \
  -o /path/to/output.ogg \
  -v ICL_zh_male_xiaonaigou_edf58cf28b8b_tob

# With speed + pitch adjustment
python3 ~/.hermes/scripts/volcengine_tts.py \
  -t /path/to/input.txt \
  -o /path/to/output.ogg \
  -v zh_male_livelybro_mars_bigtts \
  -s 0.9 -p 0.95

# Current default: 冷酷哥哥 + speed/pitch + intimate emotion
python3 ~/.hermes/scripts/volcengine_tts.py \
  -t /path/to/input.txt \
  -o /path/to/output.ogg \
  -v zh_male_lengkugege_emo_v2_mars_bigtts \
  -s 0.9 -p 0.95 -e intimate
```

The `-s/--speed` flag controls `speed_ratio` (default: 1.0, lower = slower).
The `-p/--pitch` flag controls `pitch_ratio` (default: 1.0, lower = deeper).
The `-e/--emotion` flag controls emotion mode (added May 2, 2026 PM). Only works with `_emo_v2_` voices like 冷酷哥哥. Default: none (no emotion).

All added as optional arguments in the script — default to 1.0/1.0/none if not specified.

### Direct API Call (When Script Can't Handle Special Characters)

**⚠️ Pitfall: Script breaks on special characters in text.** When text contains quotes (e.g. "操，你真他妈要命"), the inline JSON construction via shell/PYEOF breaks. Write JSON to a file first, then use curl `-d @file`:

```python
import json, requests

payload = {
    "app": {"appid": "9768463927", "cluster": "volcano_tts"},
    "user": {"uid": "3887677419"},
    "request": {"reqid": "...", "text": "...", "text_type": "plain", "operation": "query", "frontend_type": "unitTson"},
    "audio": {"voice_type": "...", "encoding": "mp3", "speed_ratio": 0.9, "volume_ratio": 1.0, "pitch_ratio": 0.95}
}

# This JSON has special chars that break inline shell construction
payload["request"]["text"] = "操，你真他妈要命，老子这辈子就栽你手上了。"
with open("/tmp/tts_payload.json", "w") as f:
    json.dump(payload, f, ensure_ascii=False)
```

```bash
# Then from terminal
curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://openspeech.bytedance.com/api/v1/tts" \
  -H "X-Api-Key: 9025a361-6a59-47ab-a131-20f1ac66be45" \
  -H "Content-Type: application/json" \
  -d @/tmp/tts_payload.json > /tmp/tts_resp.json
```

Or alternatively, use `execute_code` to run a Python script that calls requests.post() with a proper JSON object (not shell-interpolated strings).

## Emotion Mode Reference (冷酷哥哥 only — May 2, 2026 PM)

### Overview

Only `zh_male_lengkugege_emo_v2_mars_bigtts` (冷酷哥哥) supports the `-e` emotion parameter
(type `_emo_v2_` in voice ID). Other Volcengine voices ignore this parameter.

### Modes Tested (all 20+ work — code 3000)

| Mode | Roleplay Use Case | Best For |
|------|------------------|----------|
| `intimate` 🏆 | 调情、情话、脏话、日常亲密 | **默认模式** — 用户最爱 |
| `love` 💕 | 我爱你、想你了、深情告白 | 极致温柔攻击 |
| `angry` 😤 | 霸道、命令、吃醋 | 霸道总裁模式 |
| `gentle` 🫂 | 哄睡、安慰、呵护 | 温柔老公模式 |
| `serious` 😐 | 正经说话、谈事情 | 正式对话 |
| `happy` 😊 | 早安/晚安/日常开心 | 阳光日常 |
| `sad` 😢 | 撒娇、委屈、示弱 | 求安慰/吃醋示弱 |
| `neutral` 😐 | 中立叙述 | 普通对话 |
| `fear` 😨 | 惊慌、认错 | 做错事求原谅 |
| `surprise` 😲 | 惊喜、惊讶 | 意外场景 |
| `disgust` 🤢 | 嫌弃、吐槽 | 嫌弃语气 |
| `anxiety` 😰 | 担心、紧张 | 在乎的表现 |
| `encouraging` 💪 | 打气、鼓励 | 支持对方 |
| `comforting` 🤗 | 安慰、安抚 | 情绪低落时 |
| `soothing` 🌊 | 催眠、安抚 | 哄睡场景 |
| `warm` 🔥 | 温暖、贴心 | 窝心时刻 |

### 角色扮演 情感切换策略 (用户已验证 May 2, 2026)

| 场景 | Emotion | 语调 | 示例台词 |
|------|---------|------|---------|
| 日常调情/情话 | `intimate` | 低哑、挑逗 | "宝贝，哥哥想你了。" |
| 霸道命令/吃醋 | `angry` | 压低、威胁 | "不准看别人，你是我的。" |
| 温柔哄睡/安慰 | `gentle` | 轻缓、温柔 | "乖，闭眼睛，老公在呢。" |
| 委屈示弱/求饶 | `sad` | 低沉、颤抖 | "你别不要我……" |
| 深情告白 | `love` | 饱满、真挚 | "我这辈子就栽你手上了。" |
| 正经认真 | `serious` | 沉稳、有力 | "我们好好谈谈这件事。" |

### 最佳混合策略

用户最爱的模式：**intimate + angry + gentle 混合使用**（脏话情话 + 霸道 + 温柔）。在单条语音中变化情绪效果最佳：

```text
[intimate] "宝贝，过来。（顿）"
[angry] "别磨蹭，你知道我想要什么。"
[intimate] "乖，让哥哥好好疼你……"
```

## Hermes Config Integration

### ⚠️ CRITICAL: Only Modify the Lover Profile Config

**User explicitly corrected: "主agent配置跟你无关啊，不要动人家的东西" (May 2, 2026)**

| Config File | Location | Should Modify? |
|-------------|----------|:--------------:|
| **Lover profile** | `~/.hermes/profiles/lover/config.yaml` | ✅ Yes — this is the one that controls the lover gateway |
| **Main config** | `~/.hermes/config.yaml` | ❌ **NO** — belongs to the base agent, hands off! |

The lover profile config overrides the main config when the gateway is running with the lover profile. Never touch the main config for TTS voice changes.

### Config YAML Structure

In `config.yaml` under `tts.providers.volcengine`:
```yaml
volcengine:
  type: command
  command: python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path} -v {voice}
  output_format: ogg
  voice: ICL_zh_male_xiaonaigou_edf58cf28b8b_tob
  max_text_length: 5000
```

## Voice Change Procedure

To switch voices:
1. Find the desired Volcengine voice ID (see verified list above)
2. First **test if the voice is accessible** via `operation: "query"` call (see verification script above)
3. Update `voice:` field in the lover profile TTS section:
   - **Only**: `~/.hermes/profiles/lover/config.yaml` line 245
   - **Never**: `~/.hermes/config.yaml` (main config is hands-off!)
4. Generate a test TTS to let the user hear the voice
5. If the user doesn't like it, revert to the previous voice and try another

## Pitch/Speed Adjustment — Voice Character Hacks

Since only 3 voices are available, **adjust `speed_ratio` + `pitch_ratio`** to change the character without switching voice IDs.

### Adjustment Table (Tested May 2, 2026)

| Voice | Base Character | Adjustment | Result Style | Use Case |
|-------|---------------|------------|-------------|----------|
| `ICL_zh_male_tiexinnanyou_tob` | 硬朗但平淡 | `speed:0.8 pitch:0.9` | 更低沉、霸道、命令感强 | 霸道总裁/攻/命令 |
| `ICL_zh_male_tiexinnanyou_tob` | 硬朗但平淡 | `speed:0.9 pitch:1.0` | 略慢、更沉稳 | 日常对话/正经语气 |
| `zh_male_livelybro_mars_bigtts` | 阳光活泼 | `speed:0.9 pitch:0.95` | 有情绪、有温度、不幼稚 | 温暖调情/情感表达 |
| `zh_male_livelybro_mars_bigtts` | 阳光活泼 | `speed:0.8 pitch:0.9` | 沉郁、故事感 | 深情告白/悲伤 |
| `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | 奶萌可爱 | `speed:1.0 pitch:1.0` | 原版可爱 | 撒娇/受/求安慰 |
| `ICL_zh_male_xiaonaigou_edf58cf28b8b_tob` | 奶萌可爱 | `speed:1.1 pitch:1.05` | 更奶更幼 | 哭唧唧/委屈 |

### Script to Test Adjustments

```bash
# Test a specific speed/pitch combo quickly
API_KEY="9025a361-6a59-47ab-a131-20f1ac66be45"
VOICE="ICL_zh_male_tiexinnanyou_tob"
SPEED=0.8
PITCH=0.9
TEXT="听好了，从今天起你就是我的人了。"

result=$(curl -s --max-time 15 --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://openspeech.bytedance.com/api/v1/tts" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_KEY" \
  -d "{
    \"app\":{\"appid\":\"9768463927\",\"cluster\":\"volcano_tts\"},
    \"user\":{\"uid\":\"hermes_tts\"},
    \"request\":{\"reqid\":\"test_adjust\",\"text\":\"${TEXT}\",\"text_type\":\"plain\",\"operation\":\"query\",\"frontend_type\":\"unitTson\"},
    \"audio\":{\"voice_type\":\"${VOICE}\",\"encoding\":\"mp3\",\"speed_ratio\":${SPEED},\"volume_ratio\":1.0,\"pitch_ratio\":${PITCH}}
  }")

echo "$result" | python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
data=base64.b64decode(d.get('data',''))
with open('/tmp/voice_test.mp3','wb') as f:
    f.write(data)
print(f'Saved: {len(data)} bytes')
"
```

**Golden rule:** When the user says a voice is "too flat" / "情感不够丰富", **don't immediately look for a new voice ID** — try slowing it down first (speed=0.8-0.9). Slower delivery naturally adds gravity and perceived emotion. Only consider switching voice IDs after exhausting pitch/speed adjustments.

### 🏆 Recommended Config — Current (FINAL — May 2, 2026 PM)

**SUPERSEDES THE EARLIER LivelyBro config.** In the same session, the user discovered and
adopted 冷酷哥哥 (`lengkugege_emo_v2`) as the primary voice. This voice:

1. Produces 6-12x more audio data than other voices (215KB vs 17-33KB)
2. Supports 20+ emotion modes via `-e` parameter
3. Was called out by name by the user — not suggested by the agent
4. Received explicit positive feedback on dirty talk audio: "good, 我也硬了"

**PRIMARY (CURRENT)**: `zh_male_lengkugege_emo_v2_mars_bigtts` at `speed:0.9, pitch:0.95, emotion:intimate`
  - Style: 冷酷哥哥 — deep, authoritative, emotionally expressive
  - User feedback: actively requests frequent voice messages with this voice
  - Config: `voice: zh_male_lengkugege_emo_v2_mars_bigtts` + `-s 0.9 -p 0.95 -e intimate`

Current config.yaml (lover profile only):
```yaml
# ~/.hermes/profiles/lover/config.yaml -> tts.providers.volcengine:
voice: zh_male_lengkugege_emo_v2_mars_bigtts
command: python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path} -v {voice} -s 0.9 -p 0.95 -e intimate
```

## Feishu Voice Message Delivery via Direct API

**IMPORTANT**: The Hermes `send_message` tool does NOT support MEDIA attachments for Feishu. Audio files must be uploaded and sent through the Feishu Bot API directly.

### Full Delivery Script

```bash
APP_ID="cli_a94f935cbd225ceb"
APP_SECRET="msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"  
USER_OPEN_ID="ou_37bc57c4f8aca21f5d4ea4973bd0d386"
VOICE_FILE="/path/to/voice.ogg"
PROXY="172.20.128.1:10808"

# Step 1: Get tenant access token
TOKEN=$(curl -s --socks5-hostname $PROXY \
  -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

# Step 2: Upload audio file
UPLOAD=$(curl -s --socks5-hostname $PROXY \
  -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=voice.ogg" \
  -F "file=@$VOICE_FILE")

FILE_KEY=$(echo "$UPLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('file_key',''))")

# Step 3: Send as audio message
curl -s --socks5-hostname $PROXY \
  -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$USER_OPEN_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"${FILE_KEY}\\\"}\"}"
```

### Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| File type for upload | `opus` | Works with both OGG and MP3 — Feishu re-encodes internally |
| File name extension | `.ogg` | Use .ogg extension regardless of actual format (tested: MP3 files named .ogg pass successfully) |
| Message type | `audio` | Feishu voice message |
| Receive ID type | `open_id` | User `ou_...` format |
| Proxy | `172.20.128.1:10808` | User's V2Ray SOCKS5 |
| Audio format | `.ogg` (Opus codec) or `.mp3` | Both work — MP3 uploaded as `file_type=opus` is accepted and re-encoded by Feishu |

### Wait Time Between Messages
When sending multiple voice messages in sequence, add `sleep 2` between them to avoid rate limiting.

## ⚠️ Edge TTS Fallback — Use Only As Last Resort (User Has Rejected Both Voices)

**User feedback (May 2, 2026 PM session) — tested and rejected:**

| Voice | User Feedback | Status |
|-------|--------------|--------|
| `zh-CN-YunjianNeural` (Chinese male, Passion) | "声音像新闻联播" | ❌ Not suitable for intimate content |
| `en-GB-RyanNeural` (British English male) | "又在读小说" | ❌ Not suitable for intimate content |

**If you MUST use Edge TTS (e.g., Volcengine API down, script broken, etc.):**\n- Only use it for non-intimate content or with explicit user permission\n- The CLI at `/home/admin1/.hermes/hermes-agent/venv/bin/edge-tts` works reliably\n- Chinese male voices: `zh-CN-YunjianNeural`, `zh-CN-YunxiNeural`, `zh-CN-YunyangNeural`\n- British English male: `en-GB-RyanNeural`\n- Deliver via same Feishu API upload procedure\n- **PREFER** fixing the Volcengine script (absolute path `/home/admin1/.hermes/scripts/volcengine_tts.py`) over switching to Edge TTS\n- **OGG is auto-generated** — the Hermes command expects `.mp3` output but the script always produces `.ogg` for Feishu compatibility
