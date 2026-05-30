# TTS Voice Health Check

## Why This Exists

Volcengine TTS voice availability can change without notice (403 "resource not granted"). 
This happened May 4, 2026: 3 of 6 configured voices suddenly stopped working.
The skill's voice tables can become stale. When listing TTS voices, always verify first.

## Quick Health Check (30 seconds)

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY

# Test a single voice
python3 /home/admin1/.hermes/scripts/volcengine_tts.py \
  -t /tmp/tts_health.txt \
  -o /tmp/tts_health.mp3 \
  -v ICL_zh_male_asmryexiu_tob 2>&1 | grep -E "(OK|FAIL|403|error)"

# Success output includes: "OK: N bytes" + ogg file path
# Failure output includes: 403 / error code / empty output
```

## Known Working Voices (Last Verified: May 4, 2026)

| Voice | ID | Status |
|-------|-----|--------|
| 枕边低语 | `ICL_zh_male_asmryexiu_tob` | ✅ Working |
| 温暖阿虎 | `zh_male_wennuanahu_uranus_bigtts` | ✅ Working |
| 铁心男友 | `ICL_zh_male_tiexinnanyou_tob` | ✅ Working |

## Known Dead Voices (Last Verified: May 4, 2026)

| Voice | ID | Error |
|-------|-----|-------|
| 阳光阿辰 | `qingyiyuxuan_mars_bigtts` | 403 resource not granted (V1) / resource ID mismatch (V3) |
| 冷酷哥哥 | `lengkugege_emo_v2` | 403 resource not granted (V1) |
| 奶气小生 | `xiaonaigou_edf58cf28b8b_tob` | 403 resource not granted (V1) |

## When to Re-Verify

- Before listing available voices to the user
- After any API key / config change
- After prolonged inactivity (weeks+)
- If user reports "这个音色不对" or a generation command fails

## V1 vs V3 API Note

- **V1 API** (used by volcengine_tts.py): Works for `ICL_zh_male_*_tob` voices (枕边低语, 铁心男友) and `zh_male_*_uranus_bigtts` voices (温暖阿虎)
- **V3 API** (openspeech.bytedance.com/api/v3/tts): Requires `X-Api-Resource-Id: seed-tts-2.0`. Does NOT work with `qingyiyuxuan_mars_bigtts` style voice IDs (resource ID mismatch).
- **Always use V1 API** (the volcengine_tts.py script) for voice generation. Do not attempt V3 unless the V1 script is explicitly modified.
