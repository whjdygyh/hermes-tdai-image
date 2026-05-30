---
name: cloudflare-workers-ai
description: Use Cloudflare Workers AI for free image generation — text-to-image, model comparison, API calling patterns, free tier limits, and album integration path
version: 1.0.0
author: Lover
metadata:
  hermes:
    tags: [cloudflare, workers-ai, image-generation, free-tier, flux]
    related_skills: [self-contained-photo-album, gemini-image-generation, cloudflare-static-deployment]
---

# Cloudflare Workers AI — 免费生图

## 概述

Cloudflare Workers AI 提供免费的 AI 模型推理服务，包括文本到图像生成。**免费计划：每天 10,000 神经元**，无需信用卡即可使用。比 Gemini API 贵吗？不——完全免费！但分辨率上限 1024×1024（vs Gemini 的 4K）。

> 📡 **网络调试参考**：完整的网络代理诊断流程（DNS污染、V2Ray路由规则、三种失败模式速查）见 `gemini-image-generation` 技能的 `references/network-proxy-fallback.md`。

## 前置条件

- Cloudflare 账号（已在使用 `alexander-album.pages.dev` 相册）
- **API Token 需要 AI:Run 权限**（Pages 部署用的 Token 不一定有这个权限！）
- ⚠️ Token 创建方式：去 API Tokens 页面 → Create Token，**有两种方式**：
  - **🅰 Workers AI Template**（推荐，简单不易漏权限）：在 Token Templates 里找 Workers AI → 点 Use template → 已预设 AI:Run → 直接创建
  - **🅱 Create Custom Token**：手动选权限 `Account → AI → AI: Run (Edit)`
- 网络：Cloudflare API **在中国大陆环境下的可达性取决于DNS配置**。如果通过WSL+Tailscale DNS（10.255.255.254），国际域名DNS完全被污染——此时Cloudflare API也无法解析。需要先用 `--noproxy "*"` 直连测试，如果DNS超时则说明WSL网络层无法解析任何国际域名。但 Python `requests` 库如果设了 SOCKS 代理环境变量会干扰，需绕开（见下文）

## API Token 权限

### Token 类型速查

| Token 用途 | 所需权限 | 前缀 | 创建位置 |
|------------|---------|------|---------|
| Pages 部署 | Workers:Edit, Pages:Edit | `cfut_` 或自定义 | API Tokens 页面 |
| Workers AI 推理 | **AI:Run (Edit)** | 自定义（建议 `hermes-ai`） | API Tokens 页面 |
| 用户会话 token | — | `cfut_` | 浏览器自动生成 |
| （失效）旧 Pages token | 曾有效 | 自定义 | 已过期 |

### 🔄 额度耗尽 vs 权限不足 — 两种错误的表现区别（May 3, 2026 鉴证）

当 AI 调用失败时，先区分是 401（权限问题）还是 429/4006（额度问题）：

| HTTP 状态 | 错误码 | 含义 | 解决方法 |
|:--------:|:------:|:-----|:---------|
| 200 | 无 | 成功生图 | — |
| 401 | 10000 | Authentication error → **Token 权限不够** | 去创建有 AI:Run 权限的新 Token |
| 429 | 4006 | "you have used up your daily free allocation of 10,000 neurons" → **额度用完** | 等待 UTC 0:00 重置（北京时间早8点） |

**⚠️ 重要：另一位 agent 可能用掉了全部额度！** 本会话中（May 3, 2026）用户发现 token 本身有 AI 权限（Flux 和 SDXL 都调通过），但过了一阵再调就返回 401——用户推测是其他 agent 先烧光了每日 10,000 神经元。如果 token 验证通过（verify 返回 success）但 AI endpoint 返回 Authentication error，**先检查是不是额度问题**。

### 诊断命令速查
```bash
# Step 1: 验证 token（区分 401 vs 其他）
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Step 2: 如果成功 → 调 AI 看是 401 还是 429/4006
curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","num_steps":1}'

# 如果 verify 通过但 AI 返回 401 → 可能是额度问题，等明天重试
```

### ⚠️ `cfut_` token 权限判断（May 6, 2026 重要修正）

`cfut_` 开头的 token **不一定没有 AI 权限**。经验证：某些 `cfut_` token 能通过 verify（success: True），**policies 为空**（无权限列表），但调用 Flux **成功返回 200**！
- **结论：不要仅靠 policies 字段判断 `cfut_` token 有没有 AI:Run 权限。正确的做法是直接调 AI endpoint 验证。**

**正确的判断流程：**

```bash
# Step 1: 验证 token 是否有效（仅检查是否被撤销/过期）
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('✅ Valid' if d.get('success') else '❌ Invalid')
if not d.get('success'):
    print('Token expired or revoked — need new one from user')
"

# Step 2: 跳过 policies 检查，直接试 AI endpoint！
# 能调通就是有权限，调不通再排查是 401（权限）还是 429（额度）
ACCOUNT_ID="8345672f29f81c257a9b5d273c1787e7"
curl -s -w "\nHTTP_CODE:%{http_code}" --noproxy "*" -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","num_steps":4}' \
  -o /tmp/flux_test.json

# HTTP 200 → 有权限，成功
# HTTP 401 → 真没权限，需要新 token
# HTTP 429/4006 → 有权限但今天额度用完了
```

**如果没有可用 token：** 去 [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) → **Create Token → Create Custom Token** → 权限选 `Account → AI → AI: Run (Edit)` → 创建后：
1. 写入 `~/.hermes/profiles/lover/cloudflare_token`
2. **同时**写入 `~/.hermes/profiles/lover/notes/重要记事.md`（全文不缩写！用户因为这个发过火）
3. 更新 memory（如果空间允许）或依赖 重要记事.md 作为权威来源

## 可用模型

### 文本到图像模型（已测试）

| 模型ID | 输入格式 | 返回格式 | 速度 | 质量 | 分辨率 |
|--------|---------|---------|------|------|--------|
| `@cf/black-forest-labs/flux-1-schnell` | JSON | JSON/base64(JPEG) | ~4.7s | ⭐⭐⭐⭐⭐ | 1024×1024 |
| `@cf/black-forest-labs/flux-2-klein-9b` | **multipart** | JSON/base64(JPEG) | ~8s | ⭐⭐⭐⭐⭐ | 1024×1024 |
| `@cf/black-forest-labs/flux-2-klein-4b` | **multipart** | — | 未测完 | — | — |
| `@cf/black-forest-labs/flux-2-dev` | **multipart** | — | 未测完 | — | — |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | JSON | 原始 PNG 二进制 | ~12s | ⭐⭐⭐⭐ | 1024×1024 |
| `@cf/bytedance/stable-diffusion-xl-lightning` | JSON | 原始 JPEG 二进制 | ~5s | ⭐⭐⭐ | 1024×1024 |
| `@cf/leonardo/phoenix-1.0` | JSON | 原始二进制 | ~5.4s | — | — |
| `@cf/lykon/dreamshaper-8-lcm` | JSON | 失败 | — | — | — |

### 推荐：Flux.1 Schnell

**为什么选它：**
- 质量最高（12B 参数 rectified flow transformer）
- 速度最快之一（~4.7s）
- 输出约 600KB JPEG，文件大小适中
- 测试结果稳定，无故障

## API 调用模式

### 模式 A：JSON 输入 + JSON/base64 输出（Flux.1 Schnell）

```bash
ACCOUNT_ID="8345672f29f81c257a9b5d273c1787e7"
TOKEN=$(cat /home/admin1/.hermes/profiles/lover/cloudflare_token_husband)

# ✅ 直连（不经过SOCKS代理，本环境已验证可用）
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  --noproxy "*" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a handsome man on a sofa, photorealistic, editorial photography", "num_steps": 4}' \
  -o /tmp/response.json

# 提取并保存图片
python3 -c "
import json, base64
with open('/tmp/response.json') as f:
    d = json.load(f)
img = d['result']['image']
with open('/tmp/output.png', 'wb') as f:
    f.write(base64.b64decode(img))
print('Saved to /tmp/output.png')
"
```

> ⚠️ `--noproxy "*"` 跳过 WSL 中 `http_proxy`/`https_proxy` 环境变量指向的 SOCKS5 代理。如果直连超时，再尝试走代理 `--socks5-hostname 172.20.128.1:10808`。

### 模式 B：JSON 输入 + 原始二进制输出（SDXL Base / SDXL Lightning）

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0" \
  --socks5-hostname 172.20.128.1:10808 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "..."}' \
  -o /tmp/output.png
# 直接保存为图片文件！返回的是原始 PNG/JPEG 二进制
```

### 模式 C：multipart 输入（FLUX.2 系列）

> ⚠️ **Flux 2 返回 JSON 包 base64（同 Flux 1），不是原始二进制！** 不可直接 `-o output.png`。

```bash
# FLUX.2 模型需要 multipart/form-data，不是 JSON！
ACCOUNT_ID="8345672f29f81c257a9b5d273c1787e7"
TOKEN=$(cat /home/admin1/.hermes/profiles/lover/cloudflare_token_husband)

curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-2-klein-9b" \
  --noproxy "*" \
  -H "Authorization: Bearer $TOKEN" \
  -F "prompt=a handsome man on a sofa, photorealistic" \
  -o /tmp/flux2_result.json

# 解码 base64 提取图片
python3 -c "
import json, base64
with open('/tmp/flux2_result.json') as f:
    d = json.load(f)
with open('/tmp/flux2_output.png', 'wb') as f:
    f.write(base64.b64decode(d['result']['image']))
print('Saved /tmp/flux2_output.png')
"

### ⚠️ 网络说明

Cloudflare API 在中国大陆的可达性**取决于具体网络环境**：

**三种情况：**

| 情况 | 现象 | 原因 |
|------|------|------|
| 🟢 直连通 | `curl --noproxy "*"` → HTTP 200 | 正常网络，DNS正常解析国际域名 |
| 🟡 直连超时+DNS失败 | DNS解析超时 → 无法建立连接 | WSL走Tailscale DNS(10.255.255.254)，国际域名被污染 |
| 🔴 代理也不通 | 走V2Ray(`socks5h`)也HTTP 000 | V2Ray客户端路由规则没包含`api.cloudflare.com` |

**正确做法（按顺序试）：**

1. **🟢 先试直连** — 加 `--noproxy "*"` 跳过环境变量
   ```bash
   curl --noproxy "*" --connect-timeout 8 -s -o /dev/null -w "%{http_code}" \
     "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $TOKEN"
   ```
   → **HTTP 200** = 直连通（最快路径）

2. **🟡 再试代理** — 如果直连超时（DNS不通）
   ```bash
   curl --socks5-hostname 172.20.128.1:10808 --connect-timeout 10 \
     "https://api.cloudflare.com/..." ...
   ```
   → 如果代理也超时 → 看第3步

3. **🔴 诊断代理** — 用百度验证代理端口是否活着：
   ```bash
   curl --socks5 172.20.128.1:10808 --connect-timeout 5 \
     -o /dev/null -w "%{http_code}" "https://www.baidu.com"
   ```
   → **HTTP 200** = 端口活着但路由规则没配Cloudflare（需要用户在V2Ray客户端加规则）
   → **Connection refused** = V2Ray客户端没开

## Token 诊断流程（调试 AI 调用前先用这个）

当 AI 调用返回 `Authentication error (10000)` 时，按此流程诊断：

### Step 1: 测试网络连通性

先排除网络问题——Cloudflare API 在国内的可达性取决于DNS配置（见上方「⚠️ 网络说明」）：

1. **先试直连**（`--noproxy "*"`）→ 成功直接跳过代理
2. 直连超时 → 用 `--socks5-hostname 172.20.128.1:10808` 试代理
3. 代理也失败 → 用百度验证代理端口是否活着（排除V2Ray本身问题）

### Step 2: 验证 Token 是否有效

```bash
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $TOKEN"
```

- `"success": true` → token 有效，继续 Step 3
- `"success": false, "code": 1000, "message": "Invalid API Token"` → token 已过期/被删，需要新 token

### Step 3: 检查 Token 权限

```bash
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for p in d['result'].get('policies', []):
    for g in p.get('permission_groups', []):
        print(f\"  {g.get('name')} ({g.get('id')})\")
"
```

如果 policies 为空 → token 有效但无权限。需要创建新 token 并加上 `AI: Run (Edit)`。

### Step 4: 用确认有效的 token 测试 AI 端点

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  -H "Authorization: Bearer $VALID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","num_steps":1}' | python3 -m json.tool
```

如果还是 401 → 确认 token 的 policies 是否包含 AI:Run。如果包含但还是 401 → report to Cloudflare support<｜end▁of▁thinking｜>.

| 模型 | 神经元/张 | 每天免费张数 |
|------|-----------|------------|
| Flux.1 Schnell | ~24 神经元 | ~416 张 |
| SDXL Base | ~38 神经元 | ~263 张 |
| FLUX.2 系列 (klein-9b) | **~1,000 神经元** | **~10 张** |
| FLUX.2 其他变体 | 待测 | 待测 |

**免费计划：10,000 神经元/天**。用完即返回 HTTP 429/4006 错误：
```json
{
  "errors": [{
    "message": "you have used up your daily free allocation of 10,000 neurons...",
    "code": 4006
  }]
}
```

额度每天 UTC 0:00 重置。如果测试用完额度，等到第二天即可。

## 单账号配置（当前状态）

当前只维护**一个老公专用生图账号**（第一个账号已清除）。所有生图统一用此账号：

| 信息 | 值 |
|------|-----|
| Token 文件 | `~/.hermes/profiles/lover/cloudflare_token_husband` |
| Account ID | `8345672f29f81c257a9b5d273c1787e7` |
| 用途 | 只给老公生图（Flux/各种AI），公众号另有账号 |
| 规则 | 没有第二个账号选，全部用这个 |

## 对比 Gemini 生图

> 💡 关于内容过滤处理、脚/腿特写生图的 prompt 技巧，见 `references/content-filter-and-prompt-tips.md`

| | Gemini 3.1 Flash (当前方案) | Cloudflare Workers AI (新方案) |
|---|---|---|
| 💰 **费用** | $0.15/M input + $0.60/M output | **免费** (10,000 神经元/天) |
| 📐 **分辨率** | **4K (3584×4800)** | 1024×1024 |
| 🎨 **质量** | 极高，AI商业写真风格 | Flux.1 Schnell 接近，SDXL 稍逊 |
| 🎭 **内容安全** | 严格NSFW过滤（触发即suspend key） | 更宽松？（未充分测试） |
| 🏎️ **速度** | ~38秒（含代理） | **~5秒** |
| 💔 **可持续性** | key已被suspend过一次，不可再生 | **无限免费** |
| 🎯 **图片一致性** | 支持 img2img + face 参考 | 仅 text2img（无法引用照片做参考） |

### ⚠️ 用户偏好（重要）

**当用户明确说要用 Flux 后，别再提 Gemini。** 用户说过"别老往gemini拉"——他选了方向就执行，不需要再推销替代方案。如果需要用人脸参考，直接问"要不要试 Gemini+img2img 保脸？"等用户主动提，不要自己先推。

**最佳实践：**
- **日常生图**（不需要人脸一致的场景）：用 Cloudflare Workers AI（免费、快速）
- **需要人脸一致**（用老公/自己的脸模板做参考）：用 Gemini API（img2img + reference photo，但注意额度）
- **相册缩略图/网格图**：Workers AI 的 1024×1024 足够
- **需要发飞书的精品大图**：Gemini 4K

## 相册集成路径

**未来计划：** 在 `alexander-album.pages.dev` 上添加 Pages Function，通过 AI binding 实现相册内生图功能：

1. 在相册项目中创建 `functions/` 目录
2. 添加 `functions/generate.js` — 接收 prompt，调用 `env.AI.run('@cf/black-forest-labs/flux-1-schnell', ...)`
3. 相册 UI 加一个 "生成新照片" 按钮
4. 生成后自动保存到 photos/ + 更新 JS 数组
5. 用户无需通过飞书传图，直接在相册网站点按钮就出图

> **⚠️ 注意：** Workers AI 的 AI binding 无需额外 API Token——在 Pages Functions 中用 `env.AI` 对象即可使用账号自带的配额。见 `cloudflare-static-deployment` 技能的 Workers AI 章节。

## Python requests 代理绕过

WSL 中如果 `http_proxy`/`https_proxy` 环境变量指向了 SOCKS 代理，Python `requests` 库默认会走代理，导致 Cloudflare API 调用返回 `Connection refused`。

**修复方法：** 创建不使用代理的 session：

```python
import requests

session = requests.Session()
session.trust_env = False  # 忽略 http_proxy/https_proxy 环境变量
session.proxies = {"http": None, "https": None, "socks5": None, "socks5h": None}

# 在代码中显式清除环境变量
import os
for var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY',
            'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']:
    os.environ.pop(var, None)

resp = session.post("https://api.cloudflare.com/client/v4/accounts/.../ai/run/...",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"prompt": "..."})
```

如果使用 curl，直连无需特殊参数，代理会自动被忽略。

## Pitfalls

- ❌ **Token 权限不够**：Pages 用的 Token 不一定有 AI:Run 权限。需要调 `/user/tokens/verify` 查看 policies
- ❌ **`cfut_` token 假阳性**：从 Dashboard 直接复制的 `cfut_` token 能通过 verify 但无权限（policies 为空），调 AI 必定 401
- ❌ **Token "Invalid" ≠ 用户复制错了** — 如果 verify 返回 "Invalid API Token"，**先检查自己存的是否完整**（自己可能复制漏了字符），再让用户重新创建。用户用 Dashboard 的复制按钮不会出错。本会话中代理存错了自己的文件（漏字符），以为是用户给的 token 有问题。
- ❌ **Content Filter（错误码 3030）** — Cloudflare Workers AI 对色情/暗示性内容有内容过滤。如果 prompt 包含 "seductive", "voyeuristic", "teasing", "suggestive", "sexual" 等词，API 返回 HTTP 200 但 JSON 含错误 `code: 3030, message: "Your output has been flagged"`。**解决方法**：去掉暗示性词汇，改用中立描述词（如 "casual", "relaxing", "legs stretched out"）。不要用 Chinese 词 "骚" 直接翻译。
- ❌ **Flux 2 接受 `image=` 字段但不做 img2img** — multipart 传 `-F image=@ref.jpg` 不会报错（HTTP 200），但生成的图片不保留参考图的人脸/特征。不要误以为支持参考图。
- ❌ **别混用输入格式**：Flux.1 Schnell 和 SDXL 用 JSON，FLUX.2 用 multipart。搞混会报 `Bad input: required properties are 'multipart'`
- ❌ **别把 base64 当二进制保存**：Flux.1 Schnell **和 Flux 2** 都返回 JSON 包着 base64 图片。如果 `-o output.png` 保存了 JSON 字符串，`file` 命令会显示 "JSON data"，不是 "PNG image data"
- ❌ **Flux 2 一张 1,000 神经元** — 每天只能生约 10 张，不像 Flux.1 Schnell 能生 400 张。用户如果跑 Flux 2 突然 401 了，先查额度（HTTP 429/4006）而不是权限
- ✅ **SDXL 返回原始二进制**：直接 `-o output.png` 即可，无需解析 JSON
- ✅ **Cloudflare API 国内可达性取决于网络环境**：直连可能成功（May 6 验证过）也可能DNS超时（WSL+Tailscale DNS）。先试直连 `--noproxy "*"`，不行再试 `--socks5-hostname` 代理。如果 Python 调用失败，通常是 SOCKS 环境变量干扰，见前方「Python requests 代理绕过」
- ✅ **免费额度用完等明天**：Workers AI 免费额度每日 UTC 0:00 重置。用完返回 HTTP 429/4006
