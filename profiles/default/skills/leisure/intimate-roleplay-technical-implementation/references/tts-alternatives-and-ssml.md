# TTS Alternatives & Edge SSML Enhancement (Tested May 2, 2026)

> **⚠️ NOTE:** This reference file documents historical testing of alternative TTS voices and SSML techniques. The user has since formalized a **2-voice approved whitelist** (see `volcengine-tts-config.md` and the main skill's TTS section). This file is retained as reference for SSML technique only — do NOT use unapproved voices even if they're documented here as "tested."

## Overview

When Volcengine TTS fails to satisfy (user rejected all 3 available voices as "中学生音色"), here are the alternatives tested and their results.

## Available Options Matrix

| TTS Provider | Status | API Key | Quality | 霸道总裁 Potential |
|-------------|--------|---------|---------|:------------------:|
| **Volcengine** | ✅ Working | 9025a361-... | Basic, limited to 3 voices | ⭐⭐ (too young) |
| **Edge TTS + SSML** | ✅ Working | Free (no key) | Neural, can be enhanced | ⭐⭐⭐⭐ (with SSML) |
| **MiniMax** | ❌ Failed | LLM-only key, no TTS balance | Excellent (not accessible) | ⭐⭐⭐⭐⭐ (unusable) |
| **OpenAI TTS** | ❌ No key | Not configured | Excellent (onyx voice) | ⭐⭐⭐⭐⭐ (unusable) |
| **ElevenLabs** | ❌ No key | Not configured | Excellent | ⭐⭐⭐⭐⭐ (unusable) |
| **Mistral** | ❌ No key | Not configured | Good | ⭐⭐⭐ (unusable) |

## Edge TTS SSML Enhancement (Discovered May 2)

### The Problem
User said Edge TTS default output sounds like "老古董机器人" (old antique robot). The default Chinese neural voices sound robotic because they lack prosodic variation, emotional expression, and proper pacing.

### The Solution: SSML Override
Edge TTS supports SSML (Speech Synthesis Markup Language) with expressive styles. By crafting SSML with the `determined` style, lowered pitch, and controlled timing, the output can sound dramatically more authoritative.

### Working SSML Template — 霸道总裁

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="determined" styledegree="2">
      <prosody rate="-15%" pitch="-15%" volume="x-loud">
        [霸道台词]
      </prosody>
      <break time="300ms"/>
      <prosody rate="-10%" pitch="-10%" volume="loud">
        [后续台词]
      </prosody>
      <break time="500ms"/>
      <prosody rate="-20%" pitch="-20%" volume="x-loud">
        [压轴台词]
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
```

### SSML Parameters Explained

| Parameter | Range | Effect |
|-----------|-------|--------|
| `rate` | `-50%` to `+50%` | Negative = slower, more deliberate |
| `pitch` | `-50%` to `+50%` | Negative = deeper, more mature |
| `volume` | `silent`/`x-soft`/`soft`/`medium`/`loud`/`x-loud` | Louder = more commanding |
| `style` | See below | Changes emotional character |
| `styledegree` | `0.01` to `2.0` | Higher = more intense expression |
| `break time` | Milliseconds | Pause for emphasis between phrases |

### Chinese Voice + Style Compatibility (Tested)

| Voice | Available Styles | Best for 霸道总裁 |
|-------|-----------------|:-----------------:|
| `zh-CN-YunxiNeural` (云希) | determined, assistant, cheerful, sad, calm, angry | ⭐⭐⭐⭐⭐ determined + -15% pitch/rate |
| `zh-CN-YunyangNeural` (云扬) | determined, assistant, cheerful, sad, calm, angry | ⭐⭐⭐⭐ determined + -25% pitch (deeper but less natural) |
| `zh-CN-YunjianNeural` (云健) | friendly, assistant, cheerful | ⭐⭐⭐ Too warm, lacks edge |
| `zh-CN-YunyeNeural` (云野) | determined, assistant, cheerful | ⭐⭐⭐⭐ Deep voice but limited style selection |

**IMPORTANT**: Chinese voices do NOT support `angry` or `shouting` styles despite being listed. Only `determined`, `assistant`, `cheerful`, `sad`, `calm` work consistently.

### Generation Script

```bash
# Create SSML file
cat > /tmp/voice_ssml.xml << 'SSML'
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="zh-CN-YunxiNeural">
    <mstts:express-as style="determined" styledegree="2">
      <prosody rate="-15%" pitch="-15%" volume="x-loud">
        听好了，从今天起你就是我的人了。
      </prosody>
      <break time="300ms"/>
      <prosody rate="-10%" pitch="-10%" volume="loud">
        不准说不，不准逃跑。
      </prosody>
    </mstts:express-as>
  </voice>
</speak>
SSML

# Clear proxy to avoid connection issues
export http_proxy="" https_proxy="" ALL_PROXY="" HTTP_PROXY="" HTTPS_PROXY=""

# Generate audio (543KB output for ~8s of speech)
/home/admin1/.hermes/hermes-agent/venv/bin/edge-tts \
  -f /tmp/voice_ssml.xml \
  --write-media /tmp/output.mp3

# Convert to OGG for Feishu
ffmpeg -y -i /tmp/output.mp3 -c:a libvorbis -q:a 5 /tmp/output.ogg
```

### Notes
- Edge TTS **must NOT have proxy set** when running — it connects to Azure's China TTS endpoint which is accessible from mainland China without proxy
- Output file is ~543KB for 8s speech (vs Volcengine's ~150KB) — much richer audio data
- The `-f` flag reads SSML from a file; the `--custom` flag does NOT exist
- Edge TTS lives at `/home/admin1/.hermes/hermes-agent/venv/bin/edge-tts`

## Feishu Audio Delivery (Verified Working May 2, 2026)

**Critical fix**: The earlier version of this doc reported "Feishu audio delivery may return 0 success". This was caused by **improper JSON escaping** in the content field. The fix:

```bash
# CORRECT JSON escaping for Feishu audio messages:
# The `content` field must contain a JSON-encoded string
# Outer: {..., "content": "{\"file_key\":\"...\"}"}

# WRONG (causes null message_id):
"content": "{\\\"file_key\\\":\\\"...\\\"}"

# If using Python/curl and getting null message_id, use this pattern:
# 1. Build content as Python dict → json.dumps → string
# 2. Wrap in the outer message JSON
# 3. Use -d with properly formed string

# Verified working approach (Python → subprocess to curl):
import json, subprocess

send_data = {
    "receive_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
    "msg_type": "audio",
    "content": json.dumps({"file_key": "file_v3_..."})
}

cmd = [
    "curl", "-s", "--max-time", "15",
    "--socks5-hostname", "172.20.128.1:10808",
    "-X", "POST",
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    "-H", f"Authorization: Bearer {token}",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(send_data, ensure_ascii=False)
]
```

When properly escaped, the response has `"code": 0` with a valid `message_id` (not null).

## MiniMax TTS — Known Failure Modes

### Test Setup
```bash
# Using provider key from ~/.hermes/profiles/lover/config.yaml
# MiniMax key: sk-cp-... (125 chars, LLM-only)
# Endpoint: api.minimax.chat/v1/t2a_v2
# Correct API format (from hermes-agent tts_tool.py)
{
  "model": "speech-2.8-hd",
  "text": "...",
  "stream": false,
  "voice_setting": {
    "voice_id": "...",
    "speed": 1.0,
    "vol": 1.0,
    "pitch": 0
  },
  "audio_setting": {
    "sample_rate": 32000,
    "bitrate": 128000,
    "format": "mp3",
    "channel": 1
  }
}
```

### Test Results by Endpoint

| Endpoint | Result | Interpretation |
|----------|--------|---------------|
| `api.minimax.chat/v1/t2a_v2` | 2054: voice id not exist | Wrong key for TTS |
| `api.minimax.chat/v1/text_to_speech` | 2054: voice id not exist | Wrong format/key |
| `api.minimax.io/v1/t2a_v2` | 2049: invalid api key | Different API key system |
| `api.minimaxi.com/v1/text_to_speech` | 2013: invalid params empty field | CN endpoint wrong format |

### Voice IDs Tested (All Failed)
`male-qnqing-fast`, `male-yaqiong-fast`, `male-shaonv`, `male-botong-fast`, `male-chuanyun`, `male-chengzhi`, `male-shaoye`, `male-tianye`, `male-shengxin`, `male-yunjian`, `male-zhubo`, `male-preset-*`, `preset-male-*`, `male-qingnian`, `male-chengshu`, `male-shengyin`, `xiaoyuan` (insufficient balance), `beijing_male` (insufficient balance), and 20+ others.

### Conclusion
MiniMax TTS on this account is **dead end**. The key lacks TTS balance. Only `xiaoyuan` and `beijing_male` returned "insufficient balance" (code 1008) instead of "voice id not exist", confirming these voices exist but can't be used. Do NOT pursue MiniMax TTS further.

## Edge TTS English/British Male Voices for London Accent Roleplay (Discovered May 2, 2026)

### Use Case
User explicitly requested "伦敦腔情话" (London accent sweet talk) as a playful roleplay request. Edge TTS supports multiple British English male voices ideal for this purpose.

### Available British English Male Voices

| Voice ID | Character | Style | Best For |
|----------|-----------|-------|----------|
| `en-GB-RyanNeural` | Warm, charismatic London lad | Friendly, confident | Sweet talk, romantic confessions, flirtatious banter |
| `en-GB-ThomasNeural` | Deeper, more mature British male | Friendly, positive | More serious/romantic declarations |

### London Accent Sweet Talk Template (Tested Working)

```text
Listen 'ere my love... you're the finest thing I've ever laid me eyes on.
Every time I see ya, my heart does a little flip, swear down.
Come 'ere, let me wrap me arms round ya and never let go.
You're my queen, my everything, and don't you ever forget it.
I love ya, I do. Right proper love ya.
```

**Writing tips for London lad voice:**
- Use contractions: `'ere` (here), `ya` (you), `me` (my)
- Add filler phrases: `swear down`, `I do`, `right proper`
- Keep it slightly cheeky/confident, not overly formal
- British slang adds authenticity: `lovely`, `mate` (in romantic context), `fit` (attractive), `proper`
- End with a punchy, sincere phrase

### Generation Command

```bash
# Clear proxy first (Edge TTS reaches Azure China endpoint directly)
export http_proxy="" https_proxy="" ALL_PROXY="" HTTP_PROXY="" HTTPS_PROXY=""

# Generate with British male voice
edge-tts \
  --voice en-GB-RyanNeural \
  -f /tmp/london_sweet_talk.txt \
  --write-media /tmp/london_lover.mp3
```

### Feishu Delivery (MP3 works despite doc saying OGG-only)

The Feishu upload API accepts MP3 files when `file_type=opus` is specified:

```bash
TOKEN=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

# Upload MP3 as 'opus' type — Feishu re-encodes internally
FILE_KEY=$(curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=opus" \
  -F "file_name=english_lover.ogg" \
  -F "file=@/tmp/london_lover.mp3" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('file_key',''))")

# Send as audio message
curl -s --socks5-hostname 172.20.128.1:10808 \
  -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"ou_37bc57c4f8aca21f5d4ea4973bd0d386\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"${FILE_KEY}\\\"}\"}"
```

**Key insight:** Feishu's `im/v1/files` endpoint with `file_type=opus` accepts any audio format (MP3, OGG) and re-encodes internally. The `file_name` extension doesn't need to match the actual format. Upload MP3 → name it `.ogg` → send as `msg_type=audio` — pipeline works end-to-end.

### When to Use British vs Chinese Voices

| Scenario | Voice | Why |
|----------|-------|-----|
| Daily intimate Chinese flirting | 冷酷哥哥 (Volcengine) | Native language, user's preferred default |
| Playful London accent request | en-GB-RyanNeural (Edge TTS) | Novelty, roleplay variety, user specifically asks for it |
| English sweet talk / bedtime story | en-GB-RyanNeural (Edge TTS) | Romantic English with warm British character |
| Dirty talk / commanding | 冷酷哥哥 + emotion=angry/intimate | User specifically loves this combination |

### Pitfalls
- **Must clear proxy before edge-tts** — Edge TTS connects to Azure's China endpoint; SOCKS5 proxy interferes (`unset http_proxy` etc.)
- **No SSML needed for English voices** — `en-GB-RyanNeural` sounds natural and warm by default at normal speed/pitch
- **Feishu delivery: always use `file_type=opus`** even for MP3 files — this is the only file type Feishu accepts for voice messages
- **User expects frequent voice messages** — "要经常发语音给我" is now a standing preference; proactively use TTS for intimate interactions

## Decision Tree — When User Says Voice Isn't Good Enough

```
User: "这个声音不好听"
  │
  ├─ Volcengine current config
  │   ├─ Try speed/pitch adjust first (0.8-0.9)
  │   └─ If still "中学生音色" → Volcengine exhausted
  │
  ├─ Edge TTS default
  │   └─ "老古董机器人" → Apply SSML enhancement
  │       ├─ YunxiNeural + determined style + pitch -15%
  │       └─ If still not good → Edge TTS exhausted
  │
  └─ Premium options (all unavailable)
      ├─ MiniMax: no TTS balance on existing key
      ├─ OpenAI TTS: no API key
      ├─ ElevenLabs: no API key
      └─ Mistral TTS: no API key
```

If ALL options exhausted, tell the user honestly what's available and ask which is most tolerable for different use cases.
