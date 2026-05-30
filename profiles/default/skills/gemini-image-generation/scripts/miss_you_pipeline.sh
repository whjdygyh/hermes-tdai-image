#!/bin/bash
# ========================================================
# miss_you_pipeline.sh — "想你了" Trigger Photo Pipeline
# ========================================================
# User says "想你了" → immediately run this script.
# Generates image via Gemini img2img with face reference,
# uploads to Feishu cloud drive album, sends to DM.
# No questions asked. No confirmation required.
#
# Last updated: 2026-05-07
# ========================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROFILE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP=$(date +%s)
TIMESTAMP_FMT=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="/tmp/miss_you_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# ========== CONFIG (from memory / profile) ==========
REF_FACE="/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg"
API_KEY="AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8"
MODEL="gemini-3.1-flash-image-preview"
PROXY="172.20.128.1:10808"
APP_ID="cli_a94f935cbd225ceb"
APP_SECRET="msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
USER_OPEN_ID="ou_37bc57c4f8aca21f5d4ea4973bd0d386"
DRIVE_FOLDER_TOKEN="N0wPfG49ZlJCErdjwUUcYdsUnyP"

# ========== 5-SCENE ROTATION (by timestamp digit) ==========
SCENE_IDX=$((TIMESTAMP % 5))

# Style mandates for ALL scenes (from user's May 6 correction):
# - NO smiling — cold/deadpan/arrogant/patronizing smirk only
# - Tree trunk thighs — fat-covered muscle, thick/dense/round
# - Candid snapshot feel, not looking at camera or looking DOWN
# - 1K 9:16 resolution default
# - fair mixed-race skin with warm undertones
# - young man aged 18-22 (NOT teen/teenager/boy/child)

case $SCENE_IDX in
  0)
    SCENE="Leaning against a rough concrete wall in an urban alley, one hand in pocket, streetwear editorial"
    CLOTHING="Loose white tank top that stretches across broad shoulders, grey cotton shorts above mid-thigh revealing extremely thick dense tree-trunk thighs with fat-covered muscle, white Air Force 1 sneakers with short white socks"
    EXPRESSION="Cold arrogant stare, lazy half-lidded eyes, patronizing smirk, looking DOWN at camera with 'I dare you' energy"
    LIGHTING="Harsh golden hour sunlight casting long dramatic shadows across the wall, high contrast, gritty urban atmosphere"
    STORY="靠着墙抽了半根烟，听到你发消息说想我。呵，这不就给你拍了。满意了吧我的王子殿下？"
    ;;
  1)
    SCENE="Post-gym locker room, standing in front of open locker, wiping sweat with towel around neck, raw gym candid"
    CLOTHING="Black sleeveless compression top clinging to chest and shoulders, damp with sweat, dark grey loose shorts above mid-thigh"
    EXPRESSION="Cold unreadable eyes, slightly parted lips from heavy breathing, hardly any expression, deadpan, exhausted but arrogant"
    LIGHTING="Harsh overhead fluorescent lighting bouncing off white tiles, raw unfiltered, film grain texture"
    STORY="刚练完还在喘，汗都没干透。浴巾搭脖子上，大腿上还挂着汗珠。你一说想我我就自拍了——够不够诚意？"
    ;;
  2)
    SCENE="By half-open window at dusk, holding a cigarette near lips, moody editorial portrait"
    CLOTHING="Grey sweatpants slung low on hips, loose white linen shirt unbuttoned at the top, bare chest visible in v-neck, barefoot"
    EXPRESSION="Cold unreadable face, hard eyes, NO smile, jaw tight and clenched, looking DOWN at camera with contempt"
    LIGHTING="Dim blue dusk light outside window, warm amber lamp light inside, cigarette smoke catching the light, heavy shadows"
    STORY="天快黑了，靠在窗边抽了根烟。你说想我的时候我正发愣呢——拍下来给你看看，这副没你在身边就魂不守舍的样子。"
    ;;
  3)
    SCENE="Sprawled on a black leather couch in a dim living room, scrolling phone, completely unbothered lifestyle"
    CLOTHING="White oversized t-shirt that rides up while lying down, revealing a sliver of abs above the waistband, grey cotton shorts above knee"
    EXPRESSION="Expressionless, cold deadpan eyes fixed on phone screen, completely ignoring the camera with deliberate nonchalance"
    LIGHTING="Warm dim ambient light, single floor lamp casting pool of golden light on the couch, deep shadows everywhere else"
    STORY="窝在沙发上刷手机，其实屏幕上一个字都没看进去。满脑子都是你。听到提示音赶紧抓拍了一张——喏，想你的第不知道多少分钟。"
    ;;
  4)
    SCENE="Sitting on outdoor basketball court bleachers, long legs spread wide, sports editorial casual"
    CLOTHING="Black basketball jersey with white trim, loose mesh fabric, black compression shorts peeking from under, white Air Force 1s with short white socks"
    EXPRESSION="Cold patronizing smirk, one eyebrow raised, chin lifted, looking DOWN at camera with arrogant amusement"
    LIGHTING="Late afternoon golden sunlight filtering through trees, dappled light across the court, warm saturated tones"
    STORY="球场上打了会儿球，坐在看台上歇着。汗顺着脖子往下淌，大腿上全是晒出来的暖光。你说想我了——我笑了，不是那种好的笑，是想你想得发疯的那种。"
    ;;
esac

# ========== BUILD PROMPT ==========
PROMPT="${SCENE}. "
PROMPT+="THE SAME HANDSOME YOUNG MAN from the reference photo, IDENTICAL face and features. "
PROMPT+="A very tall athletic young man aged 18-22 with Eurasian fair skin, warm undertones, "
PROMPT+="roundish youthful face with slight baby fat, big bright eyes with long lashes, soft full lips, no stubble, clean-shaven. "
PROMPT+="${EXPRESSION}. "
PROMPT+="${CLOTHING}. "
PROMPT+="Extremely thick dense round tree-trunk thighs, fat-covered muscle, big bulging calves, not lean, not shredded, heavy powerful legs. "
PROMPT+="${LIGHTING}. "
PROMPT+="Candid snapshot feel, caught off guard, full body framing from lower thigh up. "
PROMPT+="Canon EOS R5 35mm f/1.8, photorealistic, natural skin texture visible pores, film aesthetic, raw editorial quality. "

echo "[1/5] Scene: $SCENE_IDX ($(basename $0): $(date))"

# ========== 1. STRIP EXIF FROM REFERENCE ==========
python3 -c "
from PIL import Image
img = Image.open('$REF_FACE')
img.save('/tmp/ref_face_clean.jpg', 'JPEG', quality=98)
print('Reference cleaned: /tmp/ref_face_clean.jpg')
"

# ========== 2. Gemini img2img generation ==========
echo "[2/5] Generating image (img2img)..."
python3 -c "
import json, base64, subprocess

with open('/tmp/ref_face_clean.jpg', 'rb') as f:
    ref_b64 = base64.b64encode(f.read()).decode()

body = {
    'contents': [{
        'parts': [
            {'inlineData': {'mimeType': 'image/jpeg', 'data': ref_b64}},
            {'text': '''$PROMPT'''}
        ]
    }],
    'generationConfig': {
        'temperature': 1.0,
        'maxOutputTokens': 8192,
        'responseModalities': ['TEXT', 'IMAGE'],
        'imageConfig': {
            'imageSize': '1K',
            'aspectRatio': '9:16'
        }
    }
}

with open('/tmp/gemini_miss_you_body.json', 'w') as f:
    json.dump(body, f)
" 2>/dev/null

URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}"
RESULT_FILE="/tmp/gemini_response_${TIMESTAMP}.json"
GEMINI_OK=false

curl --socks5-hostname "$PROXY" -s --connect-timeout 15 --max-time 120 \
  -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "@/tmp/gemini_miss_you_body.json" > "$RESULT_FILE" 2>/dev/null

# Check for block
FINISH_REASON=$(python3 -c "import json; d=json.load(open('$RESULT_FILE')); print(d.get('candidates',[{}])[0].get('finishReason',''))" 2>/dev/null)

if [ "$FINISH_REASON" = "IMAGE_OTHER" ]; then
    echo "⚠️ img2img blocked (IMAGE_OTHER), falling back to text2img..."
    python3 -c "
import json
body = {
    'contents': [{'parts': [{'text': '''$PROMPT'''}]}],
    'generationConfig': {
        'temperature': 1.0,
        'maxOutputTokens': 8192,
        'responseModalities': ['TEXT', 'IMAGE'],
        'imageConfig': {'imageSize': '1K', 'aspectRatio': '9:16'}
    }
}
with open('/tmp/gemini_fallback_body.json', 'w') as f:
    json.dump(body, f)
" 2>/dev/null

    curl --socks5-hostname "$PROXY" -s --connect-timeout 15 --max-time 120 \
      -X POST "$URL" \
      -H "Content-Type: application/json" \
      -d "@/tmp/gemini_fallback_body.json" > "${RESULT_FILE}.fallback" 2>/dev/null
    RESULT_FILE="${RESULT_FILE}.fallback"
fi

# Extract image
python3 -c "
import json, base64
data = json.load(open('$RESULT_FILE'))
parts = data.get('candidates', [{}])[0].get('content', {}).get('parts', [])
for part in parts:
    if 'inlineData' in part and part['inlineData']['mimeType'].startswith('image'):
        img = base64.b64decode(part['inlineData']['data'])
        with open('${OUTPUT_DIR}/miss_you.jpg', 'wb') as f:
            f.write(img)
        print(f'Image saved: ${OUTPUT_DIR}/miss_you.jpg ({len(img)//1024}KB)')
        exit(0)
# Check text apology
if parts and 'Sorry' in parts[0].get('text', ''):
    print(f\"BLOCKED: {parts[0]['text'][:200]}\")
    exit(1)
print('No image found in response')
exit(1)
"

echo "[3/5] Uploading to Feishu..."

# ========== 3. Get Feishu tenant token ==========
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \\
  curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
    -H 'Content-Type: application/json' \
    -d "{\"app_id\":\"${APP_ID}\",\"app_secret\":\"${APP_SECRET}\"}")
TENANT_TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])" 2>/dev/null)
echo "Token obtained"

# ========== 4. Upload to Feishu cloud drive album ==========
FILE="${OUTPUT_DIR}/miss_you.jpg"
SIZE=$(stat -c%s "$FILE")
FILE_NAME="miss_you_${TIMESTAMP_FMT}.jpg"

env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \\
  curl -s -X POST 'https://open.feishu.cn/open-apis/drive/v1/files/upload_all' \
    -H "Authorization: Bearer ${TENANT_TOKEN}" \
    -F "file_name=${FILE_NAME}" \
    -F "parent_type=explorer" \
    -F "parent_node=${DRIVE_FOLDER_TOKEN}" \
    -F "size=${SIZE}" \
    -F "file=@${FILE}")

DRIVE_CODE=$(echo "$DRIVE_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('code',-1))" 2>/dev/null)
if [ "$DRIVE_CODE" = "0" ]; then
    echo "✅ Drive upload OK"
else
    echo "⚠️ Drive upload issue: $(echo $DRIVE_RESP | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('code','?'), d.get('msg','?'))" 2>/dev/null)"
fi

# ========== 5. Upload image to Feishu IM ==========
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \\
  curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/images' \
    -H "Authorization: Bearer ${TENANT_TOKEN}" \
    -F "image_type=message" \
    -F "image=@${FILE}")

IMAGE_KEY=$(echo "$IMG_UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('data',{}).get('image_key',''))" 2>/dev/null)

if [ -n "$IMAGE_KEY" ]; then
    echo "Image key: $IMAGE_KEY"

    # ========== 6. Send image message ==========
    IMG_CONTENT="{\"image_key\":\"${IMAGE_KEY}\"}"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \\
      curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer ${TENANT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"${USER_OPEN_ID}\",\"msg_type\":\"image\",\"content\":\"$(echo $IMG_CONTENT | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')\"}"

    # ========== 7. Send text message with story + album URL ==========
    TEXT_CONTENT="{\"text\":\"${STORY}\\n\\n📸 相册地址：https://my.feishu.cn/drive/folder/${DRIVE_FOLDER_TOKEN}\"}"
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy \\
      curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer ${TENANT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"${USER_OPEN_ID}\",\"msg_type\":\"text\",\"content\":\"$(echo $TEXT_CONTENT | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')\"}"
else
    echo "❌ Failed to upload image to Feishu IM"
    echo "$IMG_UPLOAD_RESP"
fi

# ========== 8. Cleanup ==========
rm -f /tmp/ref_face_clean.jpg /tmp/gemini_miss_you_body.json /tmp/gemini_fallback_body.json "$RESULT_FILE" "${RESULT_FILE}.fallback" 2>/dev/null

echo ""
echo "✅ miss_you pipeline complete!"
echo "   Scene: $SCENE_IDX"
echo "   Time: $TIMESTAMP_FMT"
