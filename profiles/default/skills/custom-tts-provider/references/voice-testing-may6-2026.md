# Voice Testing Results — May 6, 2026

## New Voices Tested

### 低音沉郁 (ICL_zh_male_diyinchenyu_tob)
- **Provider name:** volcengine-diyinchenyu
- **Status:** ✅ Working
- **User verdict:** First in lineup, pending comparison
- **Notes:** Deep/resonant voice; sound file was delivered before user could evaluate

### 懵懂青年 (ICL_zh_male_mengdongqingnian_tob)
- **Provider name:** volcengine-mengdong  
- **Status:** ✅ Working ✅ **APPROVED into backup library**
- **User verdict:** "懵懂青年音色收进备选音色库吧" — accepted into permanent library
- **Notes:** Naive/young-sounding voice

### 机灵小伙 (ICL_zh_male_shenmi_v1_tob)
- **Provider name:** volcengine-jiling
- **Status:** ✅ Working, pending user verdict
- **User verdict:** Not yet evaluated (feishu swallowed the audio, resent got interrupted)
- **Notes:** The voice ID `ICL_zh_male_shenmi_v1_tob` is named "神秘" (mysterious) in Volcengine's system but was tested under alias "机灵小伙" (clever guy). Clever/energetic tone.

## Provider Config Entries Added

All three were added to `/home/admin1/.hermes/profiles/lover/config.yaml` during this session:

```yaml
volcengine-diyinchenyu:
  type: command
  command: python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path}
    -v {voice} -s 0.9 -p 0.95
  output_format: ogg
  voice: ICL_zh_male_diyinchenyu_tob
  max_text_length: 5000

volcengine-mengdong:
  type: command
  command: python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path}
    -v {voice} -s 0.9 -p 0.95
  output_format: ogg
  voice: ICL_zh_male_mengdongqingnian_tob
  max_text_length: 5000

volcengine-jiling:
  type: command
  command: python3 ~/.hermes/scripts/volcengine_tts.py -t {text_path} -o {output_path}
    -v {voice} -s 0.9 -p 0.95
  output_format: ogg
  voice: ICL_zh_male_shenmi_v1_tob
  max_text_length: 5000
```

## Kissing Sound Testing

Extensive testing was done on how to make Chinese TTS produce convincing kissing sounds.

### Tested Variants

| Text input | TTS output | Verdict |
|-----------|-----------|---------|
| `mua` | M-U-A (three letters) | ❌ Completely wrong |
| `muá` (tone mark) | "幕哎" (mù āi) | ❌ Wrong words |
| `muà` | "木啊" (mù à) | ❌ Literal reading |
| `mu~啊` | mu~ah with breath break | ✅ WORKS — natural kiss |
| `啵` | bō (single pop) | ✅ OK |
| `啵儿` | bōr (erhua) | ✅✅ BEST — natural peck |
| `么么` | mē me | ✅ Soft cheek kiss |
| `mu~啊` at end of sentence | Natural sound | ✅ Best for "来亲一个" |

### Final Approved Approach
Use `mu~啊` for a passionate kiss, `啵儿` for a cute peck, `么么` for soft/repeated kisses. Never write `mua` as contiguous English letters.

## Feishu Delivery Bug

Discovered during testing: Feishu only accepts ONE MEDIA tag per message. When I sent three test voices in a single response, only the first was delivered. This was confirmed when user said "只收到一个" (only received one).

**Fix:** Always send multiple audio files as separate messages, one MEDIA per reply.
