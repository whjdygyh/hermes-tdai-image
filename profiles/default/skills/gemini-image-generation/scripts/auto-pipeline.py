#!/usr/bin/env python3
"""
Gemini Image Generation Auto-Pipeline — Full End-to-End Script

Does in one run:
  1. Gemini img2img with face template → celebrity 4K image
  2. Save to Windows Pictures folder
  3. Upload to Feishu private chat
  4. Copy to album repo (whjdygyh/Alexander)
  5. Update index.html
  6. Git commit & push → Netlify auto-deploy

Usage:
  python3 auto-pipeline.py           # generates with default prompt
  python3 auto-pipeline.py --no-send  # generate & save only, skip Feishu/GitHub

Requirements:
  - curl installed (for Gemini API through SOCKS5 proxy)
  - requests library (for Feishu API — doesn't need PySocks since trust_env=False)
  - Git configured with PAT in ~/.git-credentials
  - Album repo cloned at REPO_DIR

Environment:
  - Runs in Hermes venv (Python 3.11.15, no PySocks)
  - Gemini API via curl --socks5-hostname 172.20.128.1:10808
  - Feishu API via requests.Session(trust_env=False)
  - Git with env vars cleared to avoid proxy conflict

Config — EDIT THESE before running:
"""

import base64, json, os, subprocess, shutil, sys
from datetime import datetime

# ===== CONFIG — EDIT ME =====
API_KEY = "AIzaSyAxKhE5IGOffTS4qUpgBZgtQyMXw1Gt_u8"
MODEL = "gemini-3.1-flash-image-preview"
FACE_REF = "/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg"
OUTPUT_DIR = "/mnt/c/Users/Administrator/Pictures/"
FEISHU_APP_ID = "cli_a94f935cbd225ceb"
FEISHU_APP_SECRET = "msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
FEISHU_OPEN_ID = "ou_37bc57c4f8aca21f5d4ea4973bd0d386"
REPO_DIR = "/home/admin1/alexander_repo/"
SITE_URL = "https://alexander-album.pages.dev/"
PROXY = "172.20.128.1:10808"  # V2Ray SOCKS5

# ===== PROMPT — EDIT ME =====
PROMPT = (
    "A candid evening snapshot of THE SAME HANDSOME YOUNG MAN from the reference photo, "
    "IDENTICAL face and features, early 20s with smooth fair skin, "
    "lounging sideways on a sofa at home in the evening, "
    "wearing a loose white t-shirt and very short grey cotton home shorts above the knee, "
    "whole body visible from head to feet in one frame, "
    "both legs stretched out along the sofa showing strong athletic thighs with thick masculine leg hair, "
    "bare feet clearly visible at the end of the sofa with natural toes, "
    "one arm resting behind his head, the other holding his phone resting on his stomach, "
    "looking down at his phone with a relaxed expression, face illuminated by phone screen glow, "
    "warm dim indoor lamplight in the background, no daylight, "
    "soft shadows on his muscular legs from the lamp light, "
    "candid moment, not posing for the camera, "
    "like someone on the other end of the sofa took this photo of him, "
    "authentic home snapshot style, not a photoshoot, "
    "natural home atmosphere, slightly messy hair, relaxed after a long day, "
    "full body composition, feet at one end of frame, head at the other, "
    "natural skin texture, warm cozy evening vibe"
)

# ===== STEP 1: Gemini img2img via curl + subprocess =====
def generate_image(ts):
    print("📸 读取脸模板...")
    with open(FACE_REF, 'rb') as f:
        ref_b64 = base64.b64encode(f.read()).decode()

    body = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": "image/jpeg", "data": ref_b64}},
                {"text": PROMPT}
            ]
        }],
        "generationConfig": {
            "temperature": 1.0,
            "maxOutputTokens": 8192,
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "imageSize": "4K",
                "aspectRatio": "3:4"
            }
        }
    }

    body_path = "/tmp/gemini_body.json"
    with open(body_path, 'w') as f:
        json.dump(body, f)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

    print("📸 生成中，调用Gemini API...")
    curl_cmd = [
        "curl", "--socks5-hostname", PROXY,
        "-s", "--connect-timeout", "15", "--max-time", "120",
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", f"@{body_path}"
    ]
    result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=130)
    if result.returncode != 0:
        print(f"❌ curl调用失败: {result.stderr[:200]}")
        sys.exit(1)

    data = json.loads(result.stdout)
    image_data = None
    if 'candidates' in data:
        for part in data['candidates'][0]['content']['parts']:
            if 'inlineData' in part and part['inlineData']['mimeType'].startswith('image'):
                image_data = base64.b64decode(part['inlineData']['data'])
                break

    if not image_data:
        print("❌ 未获取到图片数据")
        if 'candidates' in data:
            for part in data['candidates'][0]['content']['parts']:
                if 'text' in part:
                    print(f"返回: {part['text'][:300]}")
        sys.exit(1)

    output_name = f"evening_candid_{ts}.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(image_data)
    file_kb = len(image_data) / 1024
    print(f"✅ 图片已保存 ({file_kb:.0f}KB): {output_path}")
    return output_path, output_name


# ===== STEP 2: Send to Feishu =====
def send_to_feishu(file_path, file_name):
    print("📤 发送飞书...")
    import requests
    sess = requests.Session()
    sess.trust_env = False  # critical: don't use SOCKS5 proxy

    # Get token
    auth_r = sess.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    tok = auth_r.json().get("tenant_access_token")
    if not tok:
        print("❌ 飞书token失败")
        return None
    print("  ✅ 飞书token获取成功")

    # Upload
    with open(file_path, 'rb') as f:
        up = sess.post("https://open.feishu.cn/open-apis/im/v1/images",
            headers={"Authorization": f"Bearer {tok}"},
            files={"image": (file_name, f, "image/jpeg")},
            data={"image_type": "message"}, timeout=30)
    up_d = up.json()
    if up_d.get("code") != 0:
        print(f"❌ 上传失败: {up_d}")
        return None
    img_key = up_d["data"]["image_key"]
    print("  ✅ 图片上传成功")

    # Send
    msg_r = sess.post("https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        json={"receive_id": FEISHU_OPEN_ID, "msg_type": "image",
              "content": json.dumps({"image_key": img_key})}, timeout=10)
    if msg_r.json().get("code") == 0:
        print("  ✅ 图片已发送到飞书私聊！")
        return True
    else:
        print(f"  ⚠️ 发送结果: {msg_r.json()}")
        return None


# ===== STEP 3: Update album repo =====
def update_album(file_path):
    print("📁 更新相册...")
    photos_dir = os.path.join(REPO_DIR, "photos/")
    os.makedirs(photos_dir, exist_ok=True)

    existing = sorted([f for f in os.listdir(photos_dir) if f.endswith('.jpg')])
    next_num = len(existing) + 1
    photo_name = f"{next_num:02d}_evening_candid.jpg"
    photo_path = os.path.join(photos_dir, photo_name)
    shutil.copy2(file_path, photo_path)
    print(f"  ✅ 已复制: {photo_name}")

    # Update index.html
    index_path = os.path.join(REPO_DIR, "index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    photo_entry = f"""            <div class="photo-item" onclick="openLightbox(this)">
                <img src="photos/{photo_name}" loading="lazy" alt="照片 {next_num}">
            </div>
"""

    for marker in ['<div class="lightbox"', '<script>', '</main>']:
        if marker in html:
            html = html.replace(marker, f'{photo_entry}\n            {marker}')
            break

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  ✅ index.html已更新")

    # Git commit & push
    print("📤 推送到GitHub...")
    os.chdir(REPO_DIR)
    env_clean = {k: v for k, v in os.environ.items()
                 if k.lower() not in ('http_proxy', 'https_proxy')}

    subprocess.run(["git", "add", f"photos/{photo_name}", "index.html"],
                   capture_output=True, env=env_clean)
    subprocess.run(["git", "commit", "-m", f"add {photo_name}"],
                   capture_output=True, env=env_clean)
    push = subprocess.run(["git", "push", "origin", "main"],
                          capture_output=True, text=True, env=env_clean, timeout=60)

    if push.returncode == 0:
        print("  ✅ GitHub推送成功！")
        return f"{SITE_URL}"
    else:
        print(f"  ⚠️ push: {push.stderr.strip()[:100]}")
        return SITE_URL


# ===== MAIN =====
if __name__ == "__main__":
    ts = datetime.now().strftime('%H%M%S')

    # Check for --no-send flag
    no_send = "--no-send" in sys.argv

    # Step 1: Generate
    output_path, output_name = generate_image(ts)

    # Step 2: Feishu (skip if --no-send)
    if not no_send:
        send_to_feishu(output_path, output_name)
    else:
        print("⏭️ 跳过飞书和GitHub (--no-send)")

    # Step 3: GitHub + Netlify
    if not no_send:
        url = update_album(output_path)
        print(f"\n🎉 全部完成！")
        print(f"🔗 相册：{url}")
    else:
        print(f"\n✅ 生成完成！")
        print(f"📁 {output_path}")
