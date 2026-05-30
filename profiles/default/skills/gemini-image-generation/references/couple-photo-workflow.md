# 双人合照生成工作流（Dual-Reference Couple Photo）

## 场景
用户希望生成**自己和伴侣**的合照，要求两个人的脸都正确、神似。

## 核心技巧：同时传入两张参考图

Gemini API 支持在一个 `contents[0].parts` 数组中传入**多个 `inlineData`**。将：
1. **用户本人的照片**（近期自拍/真人照）作为第一张参考图
2. **伴侣的固定脸模板**（如 `athlete_face_front.jpg`）作为第二张参考图
3. 然后在下一个 `{"text": prompt}` 中分别描述「两个人在合照中应该长什么样」

## 验证可行流程（May 2, 2026）

### 前置条件
- 用户本人的照片：`/home/admin1/.hermes/profiles/lover/cache/images/img_601da2be6fce.jpg`（用户自拍）
- 伴侣的脸模板：`/mnt/c/Users/Administrator/Documents/abots/lover_portraits/athlete_face_front.jpg`
- 两张图都编码为 base64，按顺序传入 `parts` 数组

### 提示词结构（关键）

必须**在 prompt 中明确对应**每张参考图对应的人：

```python
PROMPT = (
    "These reference photos show the TWO individuals who should appear together:\n\n"
    "REFERENCE 1 (the OLDER MAN): A handsome mature man around 45 years old, "
    "strong masculine features, [详细描述], "
    "THE SAME PERSON from the first reference photo, identical face and features.\n\n"
    "REFERENCE 2 (the YOUNG BOYFRIEND): An extremely handsome 18-20 year old "
    "mixed-race teenage boy with very fair skin, "
    "the SAME PERSON from the second reference photo, identical face and features, "
    "[详细描述].\n\n"
    "[场景描述：构图、服装、光线、氛围]\n"
    "[摄影风格关键词]"
)
```

### 验证过的提示词示例

#### 咖啡店合照（成功）
```python
PROMPT = (
    "Create a warm candid couple selfie of two lovers at a coffee shop in the late morning. "
    "These reference photos show the TWO individuals who should appear together:\n\n"
    "REFERENCE 1 (the MAN sitting at the table): A handsome mature man around 45 years old, "
    "strong masculine features, slight stubble, wearing a casual shirt, warm relaxed expression, "
    "THE SAME PERSON from the first reference photo, identical face and features.\n\n"
    "REFERENCE 2 (his YOUNG BOYFRIEND sitting across from him): An extremely handsome 18-20 year old "
    "very fair-skinned mixed-race athletic teenage boy, the SAME PERSON from the second reference photo, "
    "identical face and features, smooth youthful skin with slight baby fat, big bright eyes, soft full lips, "
    "completely clean-shaven, mischievous warm smile, looking at the older man with adoration.\n\n"
    "Composition: Both sitting at a small round cafe table, taken as a POV selfie shot "
    "from just behind the younger boy's shoulder looking toward the older man. "
    "The older man is in focus at the table, warm espresso and latte cups on the table between them. "
    "The younger boy's shoulder and the side of his face visible at the edge of frame "
    "(he's the one taking the selfie). "
    "Warm indoor cafe lighting, soft natural light from a large window, "
    "cozy coffee shop atmosphere. "
    "Authentic couple moment, natural intimacy, the older man smiling warmly at the younger boy. "
    "Phone selfie quality, slightly imperfect composition, real life couple moment, "
    "award winning portrait photography, photorealistic, natural skin texture."
)
```

#### 夏天咖啡店合照（验证通过）
```python
PROMPT = (
    "A warm sunny summer day couple photo at an outdoor cafe terrace. "
    "These reference photos show the TWO individuals who should appear together:\n\n"
    "REFERENCE 1 (the OLDER MAN): A handsome mature man around 45 years old, "
    "strong masculine face, slight stubble, short dark hair, "
    "wearing a loose white linen short-sleeve summer shirt, first two buttons open, "
    "relaxed and happy, THE SAME PERSON from the first reference photo, identical face and features.\n\n"
    "REFERENCE 2 (the YOUNG BOYFRIEND): An extremely handsome very young 18-20 year old "
    "mixed-race teenage boy with very fair skin, the SAME PERSON from the second reference photo, "
    "identical face and features, smooth youthful skin with slight baby fat, big bright eyes, "
    "mischievous smile, wearing a white cotton t-shirt, sitting close to the older man.\n\n"
    "Composition: A genuine loving couple sitting side by side at a small outdoor cafe table. "
    "The younger boy is leaning against the older man's shoulder playfully. "
    "The older man has his arm around the younger boy's shoulder/waist, "
    "both looking toward the camera with warm genuine smiles. "
    "Iced coffee and a cold drink on the table, summer afternoon, "
    "dappled sunlight through tree leaves creating soft shadows on their faces. "
    "Bright summer atmosphere, blue sky visible behind them. "
    "Slightly warm golden afternoon light, iced drinks with condensation on the glasses. "
    "Authentic couple moment, happy summer vibe. "
    "Canon EOS R5 50mm f/1.8, natural summer lighting, "
    "photorealistic, award winning lifestyle couple portrait photography."
)
```

### 输出结果
- 两轮生成都成功（未触发 IMAGE_OTHER 过滤）
- 分辨率：**3584×4800**（4K, 3:4）
- 文件大小：~7.4-7.8MB 每张
- 照片中两个人的脸分别近似两张参考图，但非100%完全一致
- 用户反馈：接受并进一步要求"夏天"版本

### 局限性
1. **面容一致性不是100%**——Gemini 会混合两张参考图的面部特征，不完全像任何一张
2. **无法控制精确位置**——构图由 Gemini 决定，无法指定「左边是谁右边是谁」
3. **风格差异大**——如果两张参考图风格差距大（一张正式一张随意），混合效果不稳定
4. **用户本人的照片质量很重要**——低像素/遮挡多的照片会影响结果

### 快速生成脚本模板

```python
import base64, json, subprocess

API_KEY = "YOUR_KEY"
MODEL = "gemini-3.1-flash-image-preview"
PROXY = "172.20.128.1:10808"

with open("user_photo.jpg", 'rb') as f:
    user_b64 = base64.b64encode(f.read()).decode()
with open("partner_template.jpg", 'rb') as f:
    partner_b64 = base64.b64encode(f.read()).decode()

body = {
    "contents": [{
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": user_b64}},
            {"inlineData": {"mimeType": "image/jpeg", "data": partner_b64}},
            {"text": PROMPT}
        ]
    }],
    "generationConfig": {
        "temperature": 1.0,
        "maxOutputTokens": 8192,
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"imageSize": "4K", "aspectRatio": "3:4"}
    }
}

body_path = "/tmp/gemini_body.json"
with open(body_path, 'w', encoding='utf-8') as f:
    json.dump(body, f, ensure_ascii=False)

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
result = subprocess.run([
    "curl", "--socks5-hostname", PROXY,
    "-s", "--connect-timeout", "15", "--max-time", "120",
    "-X", "POST", url,
    "-H", "Content-Type: application/json",
    "-d", f"@{body_path}"
], capture_output=True, text=True, timeout=130)

data = json.loads(result.stdout)
for part in data['candidates'][0]['content']['parts']:
    if 'inlineData' in part and 'image' in part['inlineData']['mimeType']:
        img_data = base64.b64decode(part['inlineData']['data'])
        with open("couple_photo.jpg", 'wb') as f:
            f.write(img_data)
        print(f"✅ Couple photo: {len(img_data)/1024:.0f}KB")
```

## 注意事项
- 不要尝试让 Gemini 画中文文字（标牌、咖啡杯上的字等）——乱码
- 用户喝美式（咖啡场景的杯子要是热美式杯或冰美式透明杯，不是拿铁杯型）
- 用户乳糖不耐受，不喝含奶咖啡
