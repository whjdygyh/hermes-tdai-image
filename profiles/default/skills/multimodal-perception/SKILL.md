---
name: multimodal-perception
description: >
  多模态感知能力 — 看图(视觉识别)、听声音(语音转录)、说话(TTS语音合成)。
  所有能力通过 Gemini API (via $GOOGLE_API_KEY) 实现，无需额外配置。
  当用户发送图片、语音消息、或要求"说话"/"看这张图"时加载此技能。
tags: [vision, image-understanding, stt, tts, voice, multimodal, gemini]
---

# 多模态感知技能

此技能赋予 Agent 三种核心感知能力：**看、听、说**。

---

## 一、看图（视觉识别）

当用户发送图片或说"你看看这张图"时，使用 Gemini Vision API 分析图片。

### API 端点
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY
```

### Python 实现
```python
import requests, json, os, base64

API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def analyze_image(image_path: str, question: str = "描述这张图片") -> str:
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # Determine mime type
    if image_path.endswith(".png"):
        mime = "image/png"
    elif image_path.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    else:
        mime = "image/webp"
    
    body = {
        "contents": [{
            "parts": [
                {"text": question},
                {"inline_data": {"mime_type": mime, "data": img_b64}}
            ]
        }]
    }
    
    resp = requests.post(URL, json=body, timeout=30)
    result = resp.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]
```

---

## 二、说话（TTS 语音合成）

当用户要求"说话"或"说一句..."时，使用 Gemini TTS 生成语音。

默认使用 `/opt/data/scripts/gemini_tts.py` 脚本，通过 `$GOOGLE_API_KEY` 调用 Gemini TTS API。
也支持火山引擎 TTS（通过 `$VOLC_API_KEY`），主配置在 config.yaml 的 `tts` 段。

### 用法
- 用户说"说话"或"说句话听听" → 使用默认 TTS 提供商生成语音
- 用户说"用暖男声音说话" → 切换为 volcengine-warm 音色
- TTS 输出会自动转为 OGG 格式适配飞书语音消息

---

## 三、听（语音转录）

当用户发送语音消息时，Hermes 自动转录文字。已配置的 STT 提供商：
- **本地 Whisper**（`base` 模型，离线可用）
- **Mistral Voxtral**（云端，需 $MISTRAL_API_KEY）
- 飞书平台直接下发语音消息的转录文本

### 重要
- **不需要额外配置** — STT 已在 config.yaml 中启用
- 用户发语音消息，Agent 自动看到文字内容并回复
- 如果语音转录失败，可以请用户用文字重发

---

## 环境变量依赖

| 变量 | 用途 | 必需 |
|------|------|------|
| `GOOGLE_API_KEY` | Gemini Vision（看图）+ Gemini TTS（说话） | ✅ |
| `VOLC_API_KEY` | 火山引擎 TTS（8 种中文男声音色备用） | ❌ |
