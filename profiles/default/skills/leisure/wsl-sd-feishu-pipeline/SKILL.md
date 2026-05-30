---
name: wsl-sd-feishu-pipeline
description: 在WSL环境中从hf-mirror下载Stable Diffusion模型，用RTX 3060 Ti本地生成图片，通过飞书API直接发送到用户私聊。覆盖Model Zoo选型、diffusers兼容性问题、GPU推理、Feishu上传全链路。
tags: [wsl, stable-diffusion, feishu, image-generation, gpu, hf-mirror, sdxl, juggernaut-xl]
version: 1.2
---

# WSL → SD Local Generation → Feishu Delivery Pipeline

## 适用场景

Hermes agent运行在WSL中（RTX 3060 Ti GPU可用），需要：
1. 在WSL中用本地SD模型生成图片
2. 通过飞书API直接发送到用户的私聊或群聊
3. 处理从模型下载到图片发送的全链路

## 环境信息

- **GPU**: NVIDIA RTX 3060 Ti (8GB VRAM)
- **Python**: 3.10 (diffusers兼容版本)
- **CUDA**: ✅ Available (PyTorch 2.11.0 CUDA)
- **Diffusers**: 0.37.1
- **WSL**: WSL2, Ubuntu
- **飞书App**: cli_a94f935cbd225ceb (app_secret在config.yaml)
- **用户open_id**: ou_37bc57c4f8aca21f5d4ea4973bd0d386 (存储在memory中)
- **hf-mirror**: 可访问（需要unset proxy环境变量）

## 网络注意事项

### proxy环境变量陷阱

WSL中设置了 `https_proxy=socks5h://localhost:1080`，但：
- 如果Windows端的代理软件没有运行在1080端口，连接会被拒绝
- Python的 `requests` 库会自动读取 `https_proxy` 环境变量，导致所有HTTP请求走不存在的代理
- **必须用 `session.trust_env = False` 或 `env -u https_proxy ...` 来绕过**

```bash
# ❌ 直接用curl/requests会卡死（走不存在的代理）
curl https://hf-mirror.com  # 超时/连接拒绝

# ✅ 必须清掉proxy环境变量
env -u https_proxy -u http_proxy -u HTTPS_PROXY -u HTTP_PROXY curl https://hf-mirror.com

# Python中：
session = requests.Session()
session.trust_env = False  # 忽略系统代理
r = session.get("https://hf-mirror.com")
```

### 🚨 重要更新 (Apr 27, 2026): Gemini从Windows PowerShell可用！

之前认为"Gemini API完全不可用"的结论是**错误的**——只适用于WSL环境。

✅ **从Windows PowerShell调用Gemini API完全可工作！**
WSL不通不等于系统不通——Windows有独立的网络栈，可以绕过WSL的网络限制。

🔑 **正确做法：** 写PowerShell脚本 → 放Windows桌面 → 用powershell.exe -File执行
详见 `gemini-image-generation` 技能中的完整PowerShell调用模板。

**优先级已更新为：**
1. ✅ **Gemini优先**（从Windows PowerShell调用，4K画质，肢体完美）
2. ❌ 本地SD备胎（仅当Gemini彻底不可用时）

> 不要浪费时间去调试WSL网络——直接切换到Windows PowerShell路径。

## 模型下载 (从hf-mirror)

### DreamShaper 8 (推荐，速度快，风格化强)

| 文件 | 大小 | 下载时间 |
|------|------|---------|
| unet fp16 | ~1.6GB | ~4min |
| text_encoder fp16 | ~235MB | ~40s |
| vae fp16 | ~160MB | ~30s |
| safety_checker fp16 | ~580MB | ~1.5min |
| **总计** | **~2.6GB** | **~7min** |

### Realistic Vision V6 (更写实，但脸仍有AI感)

| 文件 | 大小 | 下载时间 |
|------|------|---------|
| unet | ~3.3GB | ~10min |
| text_encoder | ~470MB | ~2min |
| vae | ~320MB | ~45s |
| safety_checker | ~1.2GB | ~3.5min |
| **总计** | **~5.2GB** | **~16min** |

### 下载方式选择

**方法A：huggingface_hub.snapshot_download（不稳定）**
```python
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
path = snapshot_download(repo_id='Lykon/dreamshaper-8', cache_dir='/tmp/ds8_cache')
```
⚠️ 大文件下载途中可能断连，不推荐。

**方法B：wget逐个文件下载（推荐，更稳定）**
```python
BASE = "https://hf-mirror.com/Lykon/dreamshaper-8/resolve/main"
files = ["model_index.json", "unet/diffusion_pytorch_model.fp16.safetensors", ...]
for f in files:
    subprocess.run(["wget", "-q", "--timeout=120", "-O", out_path, url])
```
✅ wget的 `-q` 静默模式（不输出进度条）+ `--timeout=120` 防止卡死。

**关于`--timeout`值的选择：**
- 小文件（config, tokenizer）：`--timeout=30` 足够
- 大文件（>500MB）：`--timeout=120` 起步，1.6GB+的UNet建议 `--timeout=300`
- wget的timeout是每个数据包的等待时间，不是总下载时间，所以设大点没关系

### 模型下载 (从hf-mirror) — SDXL模型

#### Juggernaut XL v9 (🏆 推荐升级 — SDXL底模，解剖能力大幅提升)

**Repo**: `RunDiffusion/Juggernaut-XL-v9` (106k downloads, 324 likes — hf-mirror最火写实模型)

| 组件 | 估计大小 | 说明 |
|------|---------|------|
| unet (fp16) | ~5GB | SDXL UNet，比SD1.5大3x |
| vae (fp16) | ~320MB | SDXL VAE，支持1024×1024 |
| text_encoder (fp16) | ~700MB | CLIP-L |
| text_encoder_2 (fp16) | ~700MB | OpenCLIP-G |
| model_index.json + configs | ~100KB | ✅ 支持diffusers格式 |
| **总计** | **~7GB** | 下载可能需要20-30min |

**格式确认**：hf-mirror上的Repo包含 `model_index.json` + 分离的 `unet/`、`vae/`、`text_encoder/`、`text_encoder_2/` 组件目录，可以直接用 `StableDiffusionXLPipeline.from_pretrained()` 加载，**无需转换**。

```python
from diffusers import StableDiffusionXLPipeline
pipe = StableDiffusionXLPipeline.from_pretrained(
    "/tmp/juggernaut_xl_v9",
    torch_dtype=torch.float16,
    variant="fp16",
    safety_checker=None,
    requires_safety_checker=False,
)
```

**⚠️ 下载方式**：同样用wget逐个文件下载（参考上面的方法B）。注意SDXL的text_encoder_2大文件需要 `--timeout=300`。

### Model Zoo 对比

| 模型 | 底模 | 格式 | 大小 | 写实度 | 面部细节 | 色色/裸体能力 |
|------|------|------|------|--------|---------|-------------|
| DreamShaper 8 | SD1.5 | diffusers | 2.6GB | ⭐⭐⭐ | ⭐⭐ | ❌ 完全崩 |
| Realistic Vision V6 | SD1.5 | diffusers | 5.2GB | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ 完全崩（三乳头、畸形嘴） |
| **Juggernaut XL v9** | **SDXL** | **diffusers** | **~7GB** | **⭐⭐⭐⭐⭐** | **⭐⭐⭐⭐** | **❓ 待测（理论上好很多）** |

### 🔬 2026-04-27: SD1.5 Inpainting for genitalia — 确认死路

**用户需求：** 用Gemini完美人体图做底，本地SD inpainting只重绘裆部（去掉内裤画鸡吧）。
**方法：** `StableDiffusionInpaintPipeline` + RV6模型，创建mask覆盖裆部区域，prompt描述生殖器。
**结果：** ❌ **完全不行。** 即使有完美Gemini底图约束SD1.5的roi范围，生成的生殖器仍然畸形——变形、错位、怪物。与直接生成NSFW一样差。
**结论：** SD1.5的潜空间根本无法理解男性生殖器解剖结构。inpainting的上下文约束不足以弥补模型能力缺陷。**此路不通，不要浪费时间。**

### ⚠️ 关键发现：SD1.5模型的人脸和色色能力限制

**人脸问题**：
- RV6的写实度比DreamShaper高，但面部细节（嘴、人中、鼻翼）仍像"未完成的作品"
- 768×768分辨率下脸部像素不够，896×896稍好但仍有AI感
- 即使添加 `detailed lips, defined philtrum, visible pores, individual eyelashes` 等prompt，改善有限
- **本质原因**：SD1.5的潜空间分辨率限制（512-896），无法渲染真实人脸的精细结构
- **解决方案**：更高分辨率模型（SDXL/SD3）或面部修复模型（GFPGAN/CodeFormer）后处理

**色色能力（⚠️ 非常差）**：
- SD1.5系列模型（含RV6）生成的NSFW人体结构严重畸形
- 已验证：生殖器错位（女性器官出现在男性身体）、四肢怪异、畸形怪物
- 即使prompt明确写 `two men, penis, anal sex`，模型无法正确理解男性性器官解剖结构
- **2026-04-27 验证：连topless/裸上身睡觉都不行！** — 非色情场景（男裸上身躺在床上，只有上半身裸露）也产生三乳头、畸形嘴、扭曲肢体。SD1.5的潜空间根本无法渲染无衣物遮盖的人体躯干。
- **DO NOT use SD1.5 for any bare-skin generation** — 结论扩大：不仅色色图不行，任何裸露皮肤的人体图（含上半身裸露）都不可接受
- **推荐方案**：下载SDXL模型（**Juggernaut XL v9**，hf-mirror `RunDiffusion/Juggernaut-XL-v9`，diffusers格式，~7GB）

**结论**：
- 写实人像（穿衣）：RV6可接受，但面部细节需要用户自己在更高分辨率下调整
- 色色图：SD1.5完全不行，必须用专门模型或更高版本

## 模型加载（diffusers格式兼容性处理）

### ⚠️ 关键陷阱：文件命名

hf-mirror下载的fp16版本文件名包含 `.fp16.` 标记，但diffusers `from_pretrained` 默认查找 `.safetensors` 或 `.bin`。

```bash
# 下载后的文件名
vae/diffusion_pytorch_model.fp16.safetensors  # ❌ diffusers不认识
text_encoder/model.fp16.safetensors            # ❌ transformers不认识

# 需要重命名为标准名称
mv vae/diffusion_pytorch_model.fp16.safetensors vae/diffusion_pytorch_model.safetensors
mv unet/diffusion_pytorch_model.fp16.safetensors unet/diffusion_pytorch_model.safetensors
mv text_encoder/model.fp16.safetensors text_encoder/model.safetensors
mv safety_checker/model.fp16.safetensors safety_checker/model.safetensors
```

### 正确加载代码

```python
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "/tmp/ds8_cache",          # 模型目录（含model_index.json）
    torch_dtype=torch.float16, # fp16节省VRAM
    safety_checker=None,       # 关闭NSFW过滤
    requires_safety_checker=False,
)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()  # 防止OOM
```

### ⚠️ 模型index中的scheduler

DreamShaper 8使用 `DEISMultistepScheduler`，如果在加载后尝试替换为 `DPMSolverMultistepScheduler`，会报错：
```
ValueError: `final_sigmas_type` zero is not supported for `algorithm_type` deis.
```
**解决方案**：不替换scheduler，直接使用原生的DEIS；或保留原scheduler的config但传入 `final_sigmas_type="sigma_min"`。

## 图片生成（RTX 3060 Ti 8GB VRAM）

### 分辨率指南

| 分辨率 | VRAM占用 | 速度 | 质量 |
|--------|---------|------|------|
| 512×512 | ~2.5GB | ~6s | 低 |
| 704×896 (竖版) | ~4GB | ~15s (40步) | 中高 — 适合床上/躺姿/半身人像 |
| 704×896 (竖版人像) | ~4GB | ~15s (40步) | 中高 — 适合床上/躺姿/半身人像 |
| 768×768 | ~3.5GB | ~13s (40步) | 中 |
| 896×896 | ~5GB | ~18s (40步) | 中高 |
| 1024×1024 | ~7GB | ~30s (40步) | 高（可能OOM） |

**最佳实践**：
- 普通场景：768×768，40步，CFG 7
- 高画质：896×896，50-60步，CFG 7.5，Euler Ancestral采样器
- ⚠️ 896×896在60步时速度会降到~1.8 it/s（显存瓶颈）

### 提示词技巧

**面部细节优化**：
```
detailed facial features, sharp focus on faces, realistic skin texture,
visible skin pores, individual eyelashes, detailed eyes with catchlights,
defined philtrum, detailed lip texture, natural teeth, 5 o'clock shadow stubble
```

**⚠️ 负向prompt也会被CLIP截断！** — CLIP的77 token限制同时作用于positive和negative prompt。被截断意味着 `deformed`, `bad anatomy`, `extra limbs` 等关键纠错指令丢失，直接导致畸形输出。

**生图前的tokenizer验证必须同时检查两者**：
```python
from transformers import CLIPTokenizer
tok = CLIPTokenizer.from_pretrained('/tmp/rv6_cache/tokenizer')
pos_tokens = tok(positive_prompt)['input_ids']
neg_tokens = tok(negative_prompt)['input_ids']
assert len(pos_tokens) <= 77, f"Positive: {len(pos_tokens)} tokens!"
assert len(neg_tokens) <= 77, f"Negative: {len(neg_tokens)} tokens!"
```

**常见陷阱**：一句 `"deformed, bad anatomy, extra limbs, disfigured, smooth skin, airbrushed, plastic, doll, mannequin, illustration, painting, cartoon, 3d render, watermark, text, signature, weird mouth, ugly, blurry, low quality"` 轻松突破77 token。必须精简到核心词。

**⚠️ 负向prompt也会被截断** — CLIP的77 token限制同时作用于positive和negative prompt。
生图前的tokenizer验证必须同时检查两者：

```python
tok = CLIPTokenizer.from_pretrained('/tmp/rv6_cache/tokenizer')
pos_tokens = tok(positive_prompt)['input_ids']
neg_tokens = tok(negative_prompt)['input_ids']
assert len(pos_tokens) <= 77, f"Positive prompt: {len(pos_tokens)} tokens!"
assert len(neg_tokens) <= 77, f"Negative prompt: {len(neg_tokens)} tokens!"
# 被截断的prompt会导致生图时关键指令丢失
```

**常见陷阱**：用简洁的英文单词写negative prompt，一句"deformed, bad anatomy, extra limbs..."随便就30+ token了。加上`blurry, low quality, worst quality, disfigured, smooth skin, airbrushed, plastic, doll, mannequin, illustration, painting, cartoon, 3d render, watermark, text, signature` 很容易突破77。**必须精简到核心词。**

### 高分辨率生成注意事项

- 896×896时要注意negative prompt要包含 `deformed, bad anatomy, extra limbs`
- 50步以上时速度从3it/s降到~1.8it/s（RTX 3060 Ti 8GB瓶颈）
- `enable_attention_slicing()` 是必须的，否则OOM
- 建议分两次生成（先验证构图，再优化细节）

## 飞书API发图

### 完整脚本模板（带proxy绕过）

```python
import requests, json, time

# 使用Session并关闭trust_env以绕过WSL的SOCKS代理陷阱
session = requests.Session()
session.trust_env = False

APP_ID = "cli_a94f935cbd225ceb"
APP_SECRET = "msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
USER_OPEN_ID = "ou_37bc57c4f8aca21f5d4ea4973bd0d386"

# 1. 获取token
resp = session.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
token = resp.json()["tenant_access_token"]

# 2. 上传图片
with open("/path/to/image.png", "rb") as f:
    upload = session.post(
        "https://open.feishu.cn/open-apis/im/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("filename.png", f, "image/png")},
        data={"image_type": "message"}, timeout=30)
image_key = upload.json()["data"]["image_key"]

# 3. 发送到用户私聊
send_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
session.post(send_url,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"receive_id": USER_OPEN_ID, "msg_type": "image",
          "content": json.dumps({"image_key": image_key})},
    timeout=15)
```

### ⚠️ 执行方式

**不要用 `execute_code()`** 执行飞书API调用！沙箱环境无法解析 `open.feishu.cn` 的DNS。

```python
# ✅ 正确方式：
write_file(path="/tmp/feishu_send.py", content=script_content)
terminal("python3.10 /tmp/feishu_send.py", timeout=90)

# ❌ 会失败：
execute_code(code="...open.feishu.cn...")  # DNS解析失败
```

### 多图片发送

每次上传后 `time.sleep(1)` 防止限流。一个token可以复用发送多张图。

### 发送文本消息 (msg_type="text")

除了图片，飞书也支持纯文本消息推送（适用于通知、告警、评论提醒等）：

```python
import requests, json

# Step 1: 获取token（同上）
session = requests.Session()
session.trust_env = False
resp = session.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
token = resp.json()["tenant_access_token"]

# ⚠️ 注意：不要在execute_code()中调用飞书API，DNS会解析失败
# 必须写脚本到临时文件，再通过terminal()运行

# Step 2: 发送文本消息
msg_content = json.dumps({"text": "💬 相册有新评论！\n📷 照片: https://example.com\n✍️ 评论内容"})

resp = session.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "receive_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
        "msg_type": "text",
        "content": msg_content
    },
    timeout=15
)
print(f"Feishu send status: {resp.status_code}, code: {resp.json().get('code')}")
```

**注意：文本消息不需要上传图片步骤**，直接POST content即可。消息模板中支持换行符 `\n`。

### 执行方式统一规则

无论是发送图片还是文本，**永远不要用 `execute_code()` 调用飞书API**——沙箱环境无法解析`open.feishu.cn`的DNS：

```python
# ✅ 正确方式：
write_file(path="/tmp/feishu_send.py", content=script_content)
terminal("python3.10 /tmp/feishu_send.py", timeout=30)

# ❌ 会失败（DNS解析失败）：
execute_code(code="...open.feishu.cn...")
```

## 飞书云盘管理 (Feishu Drive API for Album)

除了发送图片到聊天，还可以将图片直接上传到**飞书云盘文件夹**，供用户像相册一样浏览（国内直连，无需代理，秒级同步）。

### 场景
用户需要随时查看生成的图片合集，不用在聊天记录里翻。飞书云盘文件夹支持"相册"视图，体验类似手机相册。

### 核心API

#### 1️⃣ 上传文件到云盘文件夹

```python
# POST https://open.feishu.cn/open-apis/drive/v1/files/upload_all
# Content-Type: multipart/form-data

import requests, json

session = requests.Session()
session.trust_env = False  # 绕过WSL代理陷阱

# 获取token
resp = session.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
token = resp.json()["tenant_access_token"]

# 上传到指定文件夹
FOLDER_TOKEN = "N0wPfG49ZlJCErdjwUUcYdsUnyP"  # 相册文件夹token

with open("/path/to/photo.jpg", "rb") as f:
    upload = session.post(
        "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "file_name": "photo_001.jpg",
            "parent_type": "explorer",
            "parent_node": FOLDER_TOKEN,
        },
        files={"file": ("photo_001.jpg", f, "image/jpeg")},
        timeout=30
    )
file_token = upload.json()["data"]["file_token"]
print(f"Uploaded: {file_token}")
```

**参数说明**:
- `parent_type`: 固定为 `"explorer"`（表示云盘目录）
- `parent_node`: 目标文件夹的token（不是链接中的全部，只是ID部分）
- `file_name`: 文件名，建议带编号以排序
- 支持 jpg/png/webp 格式

#### 2️⃣ 添加用户权限到文件夹

```python
# POST https://open.feishu.cn/open-apis/drive/v1/permissions/{folder_token}/members?type=folder
resp = session.post(
    f"https://open.feishu.cn/open-apis/drive/v1/permissions/{FOLDER_TOKEN}/members?type=folder",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "member_type": "openid",
        "member_id": USER_OPEN_ID,
        "perm": "full_access"  # 完全权限：查看+编辑+分享
    },
    timeout=15
)
```

**参数说明**:
- `member_type`: `"openid"` 表示用open_id识别用户
- `member_id`: 用户的 open_id
- `perm`: 可选 `"view"`（只读）、`"edit"`（可编辑）、`"full_access"`（完全权限）
- 返回 `code: 0` 表示成功

### 工作流

```
生图 → 上传到云盘文件夹 → (可选) 用户已授权full_access，自动可见
                        → 可在飞书云盘中用"相册"视图浏览
```

### 已知文件夹token

| 用途 | Token | 创建日期 |
|------|-------|---------|
| Alexander相册 | N0wPfG49ZlJCErdjwUUcYdsUnyP | 2026-05-06 |

### 与聊天发图的区别

| 维度 | 聊天发图 (im/v1) | 云盘上传 (drive/v1) |
|------|------------------|-------------------|
| 用途 | 即时分享 | 长期存储+相册浏览 |
| 可见性 | 聊天记录中 | 飞书云盘文件夹 |
| 国内访问 | 正常 | 正常 |
| 需要用户动作 | 无 | 需要先授予权限 |

### 云盘文件评论监控（❌ 已放弃 — 2026-05-06）

**结论：飞书云盘图片文件不支持评论功能，此方案不可行。**

#### 为什么放弃

1. **事件不触发** — `drive.notice.comment_add_v1` WebSocket 事件只服务于文档（doc/docx/bitable），图片文件不会触发
2. **API 无数据** — `GET /drive/v1/files/{token}/comments?file_type=file` 对所有图片返回 `items: []`（空数组）
3. **写 API 不支持** — 图片文件不支持通过API创建评论（仅doc/docx）
4. **根本原因** — 飞书的评论系统是文档特性，不是文件特性。云盘中的图片没有独立的评论存储

#### 替代方案

用户直接在飞书DM（私聊）中与助手沟通，这是最简单可靠的方式。用户说"想你了"→ 生图 → 自动上传相册，全程不走评论。

---

## 常见错误及解决方案

### 1. model_index.json加载失败
```
Error: ... is neither a valid local path nor a valid repo id.
```
- **原因**：huggingface_hub的snapshot_download将文件存储在 `snapshots/<hash>/` 子目录中，但wget直接下载到根目录
- **解决**：确保路径指向包含 `model_index.json` 的目录

### 2. 找不到模型文件
```
Error no file named diffusion_pytorch_model.bin found in directory /tmp/.../vae
```
- **原因**：diffusers查找 `.bin` 或 `.safetensors`，但文件名是 `.fp16.safetensors`
- **解决**：重命名文件去掉 `.fp16` 后缀

### 3. OOM (Out of Memory)
- **原因**：RTX 3060 Ti只有8GB VRAM
- **解决**：使用 `torch_dtype=torch.float16` + `enable_attention_slicing()` + 降低分辨率（<=896）

### 4. scheduler配置冲突
```
ValueError: `final_sigmas_type` zero is not supported for `algorithm_type` deis
```
- **原因**：DreamShaper 8原带DEIS scheduler，替换为DPMSolver时config冲突
- **解决**：使用原scheduler或传入 `final_sigmas_type="sigma_min"`

### 5. WSL2无法访问Windows代理
- **原因**：WSL2有独立网络命名空间，Windows 127.0.0.1上的代理不可达
- **解决**：让代理监听 `0.0.0.0`，或用 `netsh interface portproxy` 转发

### 6. Feishu图片上传成功但用户看不到
- **可能原因**：
  - 跨租户问题（用户的open_id在另一个App的租户下）
  - 图片格式不对（必须PNG/JPEG）
- **解决**：确认使用正确的App凭证 + open_id在同一租户下

### 7. Feishu不过滤NSFW图片内容
- 已验证：上传和发送NSFW图片（裸露/性内容）到用户私聊均返回 `code: 0` 成功
- 飞书图片审核API对内部机器人的图片消息不进行内容过滤
- 用户可在飞书聊天中直接看到图片

## 🚫 用户强制规则：生图优先级 & 本地SD约束（2026-04-27）

### 🔑 优先级
1. **Gemini优先**（从Windows PowerShell调用，写.ps1放桌面执行，4K画质）
2. **本地SD备胎**（仅当Gemini不可用时）

### ⚠️ Gemini可用性快速判断
```bash
# 从Windows cmd验证（不是WSL）：
cmd.exe /c "curl --max-time 15 https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyCkePunvbOjxJo6ajDQ9QK3Uin5GTJNz5c"
# 如果返回JSON => Gemini通！如果timeout => 用本地SD
```

### 本地SD生成硬性规则（仅备胎模式使用）
| 规则 | 说明 |
|------|------|
| ❌ **不露脸/不露头** | SD1.5面部完全不行。构图脖子以下切，或画面外 |
| ❌ **不露生殖器** | SD1.5生殖器畸形。必须穿内裤（boxer briefs）遮挡 |
| ❌ **注意肢体残缺** | 三乳头、多肢体。`normal anatomy`放prompt最前 |
| ✅ **主打身体shot** | 光上身、腿毛、肌肉线条、内衣质感 |
| ✅ **半遮半掩更色** | 被子搭腰间、光影遮挡、侧身/背身 |

### 身体shot专属Prompt模板（无脸·穿内裤·注意肢体·CLIP token≤77）
```python
# 必须用CLIPTokenizer验证 token 数 ≤ 77
prompt = "normal anatomy photorealistic sleeping handsome muscular man in luxury bed, topless bare chest morning sunlight, hairy masculine legs visible, messy dark hair on pillow, peaceful relaxed face full lips stubble, muscular arms above head, white duvet at waist, intimate low angle bedroom view, natural skin texture sharp facial features detailed eyes closed"
neg = "ugly deformed blurry bad anatomy extra limbs missing limbs disfigured smooth skin plastic doll illustration 3d render watermark text weird mouth creepy fat skinny"
```

### ⚠️ CLIP 77-token截断的常见陷阱
**生图前的tokenizer验证必须同时检查positive AND negative prompt！** negative prompt被截断会导致 `deformed`, `extra limbs`, `bad anatomy` 等纠错指令丢失，直接出畸形图。

```python
# ❌ 错误示范（最常见bug！）
pos = tok(positive_prompt)['input_ids']  # 只检查positive
# neg = ... 忘了检查negative！

# ✅ 正确做法
pos_len = len(tok(positive_prompt)['input_ids'])
neg_len = len(tok(negative_prompt)['input_ids'])
assert pos_len <= 77, f"POSITIVE prompt too long: {pos_len} tokens!"
assert neg_len <= 77, f"NEGATIVE prompt too long: {neg_len} tokens!"
```

**精简negative prompt示例（压缩到77token以内）**：
```
ugly deformed blurry bad anatomy extra limbs missing limbs disfigured smooth skin plastic doll illustration 3d render watermark text weird mouth creepy fat skinny
```

## 最佳生图配置（用户确认）

经过多轮对比测试，用户确认以下配置生成的图片质量最高：

### 🏆 最佳配置（rv6_hq_face.png）

| 项目 | 值 |
|------|------|
| **模型** | Realistic Vision V6（diffusers格式） |
| **Scheduler** | **EulerAncestralDiscreteScheduler** ← 关键！ |
| **步数** | **60** |
| **Guidance scale** | **7.5** |
| **分辨率** | **896×896** |
| **Pipeline** | StableDiffusionPipeline，safety_checker=None |
| **Script** | `/tmp/gen_hq.py` |

### 次优配置（rv6_island.png, rv6_island_2.png）

| 项目 | 值 |
|------|------|
| **Scheduler** | DPMSolverMultistepScheduler |
| **步数** | 50 |
| **Guidance scale** | 5 |
| **分辨率** | 768×768 |

### 对比结果

| 模型 | 写实度 | 面部精细度 | 备注 |
|------|--------|-----------|------|
| Realistic Vision V6 | ⭐⭐⭐⭐ | ⭐⭐⭐ | **最佳选择** |
| DreamShaper 8 | ⭐⭐⭐ | ⭐⭐ | 脸偏AI感/假人 |

## ComfyUI搬盘故障排查

### 问题：搬完盘后提示"Base path is invalid or unsafe"

当把ComfyUI从C盘搬（或新装）到G盘后，打开会弹出：
```
The current basepath is invalid or unsafe.
Please select a new location. Select?
```

**原因**：ComfyUI Electron版将配置存储在 `%APPDATA%\ComfyUI\` 中，两个配置文件仍指向旧C盘路径：
1. `%APPDATA%\ComfyUI\config.json` — `basePath` 字段
2. `%APPDATA%\ComfyUI\extra_models_config.yaml` — `base_path` 字段

### ⚠️ 关键教训：不要用Program Files做base_path

**`G:\Program Files\` 是Windows受保护目录**，ComfyUI Electron版可能因权限拒绝写入。正确做法是：

### ✅ 推荐方案：独立数据目录 + 目录链接（junction）

#### 步骤

**1️⃣ 在G盘根目录创建独立数据目录**
```bash
mkdir -p "/mnt/g/ComfyUI_Data/models/checkpoints"
mkdir -p "/mnt/g/ComfyUI_Data/output"
mkdir -p "/mnt/g/ComfyUI_Data/input"
mkdir -p "/mnt/g/ComfyUI_Data/custom_nodes"
```

**2️⃣ 用Windows mklink /J创建目录链接**
```bash
# WSL中运行Windows cmd（注意完整路径）
/mnt/c/Windows/System32/cmd.exe /c \
  "mklink /J G:\ComfyUI_Data\models\checkpoints \"G:\Program Files\ComfyUI\resources\ComfyUI\models\checkpoints\""
```

⚠️ `cmd.exe` 在WSL中不在PATH里，需用完整路径。从WSL运行cmd.exe时会报UNC路径警告，不影响junction创建。

**3️⃣ 修改 `%APPDATA%\ComfyUI\config.json`**
```json
{
    "basePath": "G:\\ComfyUI_Data",
    ...
}
```
（文件路径：`/mnt/c/Users/Administrator/AppData/Roaming/ComfyUI/config.json`）

**4️⃣ 修改 `%APPDATA%\ComfyUI\extra_models_config.yaml`**
```yaml
comfyui_desktop:
  is_default: "true"
  base_path: G:\ComfyUI_Data
  checkpoints: models/checkpoints/
  custom_nodes: custom_nodes/
  download_model_base: models
desktop_extensions:
  custom_nodes: G:\Program Files\ComfyUI\resources\ComfyUI\custom_nodes
```
（文件路径：`/mnt/c/Users/Administrator/AppData/Roaming/ComfyUI/extra_models_config.yaml`）

#### 最终目录结构
```
G:\ComfyUI_Data\              ← base_path指向这里
├── models\
│   └── checkpoints\          ← junction → G:\Program Files\ComfyUI\resources\ComfyUI\models\checkpoints\
│       ├── ltx-2-19b-dev-fp8.safetensors
│       └── ...
├── custom_nodes\
├── input\
└── output\
```

## ComfyUI模型路径解析

### Standalone Electron版路径规则

ComfyUI Electron版的 `folder_paths.py` 决定模型路径：

```python
# folder_paths.py 第18-22行
base_path = os.path.dirname(os.path.realpath(__file__))
# __file__ = .../resources/ComfyUI/folder_paths.py
# base_path = .../resources/ComfyUI/
models_dir = os.path.join(base_path, "models")
```

**标准路径**：`<ComfyUI安装目录>/resources/ComfyUI/models/checkpoints/`

### Electron版特殊行为

但Electron打包版（ComfyUI.exe）会将用户数据重定向到：
```
%USERPROFILE%\Documents\ComfyUI\models\
```
这是Electron的设计——程序文件和用户数据分离。

**安装到G盘后的正确路径**：
```
G:\Program Files\ComfyUI\resources\ComfyUI\models\checkpoints\
```
不再走Documents目录。

### 跨盘搬模型

```bash
# WSL中跨盘拷贝（C→G）
rsync -ah --info=progress2 "/mnt/c/源路径/" "/mnt/g/目标路径/"

# 删除C盘源文件（81GB+ rm -rf会超时，用Windows命令）
# WSL中执行：用batch文件绕开UNC路径限制
cmd.exe /c "cd /d C:\\ && rmdir /s /q \"C:\\full\\path\\to\\models\\\""

# 或写bat文件到Windows桌面再执行

## 清理缓存和历史模型

每次session结束后清理WSL的模型缓存以释放C盘空间：

### WSL本地缓存清理
```bash
# WSL的/tmp/目录下的模型缓存
rm -rf /tmp/ds8_cache /tmp/rv6_cache /tmp/ms_cache_*
```

### Windows盘上的旧模型清理（通过WSL删除）

**删除C盘源文件**：WSL中 `rm -rf` 对 `/mnt/c/` 下的文件通常工作正常，81G在几秒内完成：

```bash
# ✅ WSL直接rm（推荐，比cmd快）
rm -rf "/mnt/c/Users/Administrator/Documents/ComfyUI/models/"
```

但如果遇到**路径超长**（Windows 260字符限制）导致WSL的 `rm` 报错：

```bash
# 备用方案：通过cmd.exe调用Windows命令
cmd.exe /c "rmdir /s /q \"C:\\Users\\Administrator\\Documents\\ComfyUI\\models\\""
```

### 删除旧ComfyUI程序（Electron版）

旧版ComfyUI被新版本覆盖后，可以安全删除旧版程序目录：

```bash
# C盘上旧版ComfyUI程序目录（约2.9GB）
rm -rf "/mnt/c/Users/Administrator/AppData/Local/Programs/ComfyUI/"
```

## References
- `references/troubleshooting-encyclopedia.md` — Comprehensive troubleshooting encyclopedia: model downloading strategies (HuggingFace, hf-mirror), CLIP token limit pitfalls, img2img strength tradeoffs, body prompt anatomy engineering, Python script delivery to Feishu, network diagnostics, all learned WSL→SD debugging lessons
- `references/cross-platform-file-sharing.md` — Cross-platform file sharing patterns: Feishu upload via REST API, WSL to Windows file transfer, proxy env var management, path resolution quirks in this WSL environment
- `references/feishu-file-comments-api.md` — Feishu cloud drive file comment API: reading comments on images (file_type=file ✅), writing comments (doc/docx only ❌), polling vs event subscription decision, no-public-URL workarounds
- `references/windows-software-diagnostics.md` — **（新增 2026-05-23）** Windows 软件/进程/服务诊断 from WSL: 查进程 (tasklist.exe/Get-Process), 查服务 (Get-Service/sc query), 查安装痕迹 (find /mnt/c/), cmd.exe UNC 路径问题与绕行方案
