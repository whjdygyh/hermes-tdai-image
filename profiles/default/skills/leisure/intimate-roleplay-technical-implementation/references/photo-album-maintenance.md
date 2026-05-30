# 私密相册维护 — 评论系统 + 照片删除工作流

## 概述

用户（安迪/Andy）的私密相册托管在 GitHub 仓库 `whjdygyh/Alexander`（已私有化），部署在 Cloudflare Pages。本参考文件记录相册维护的关键技术模式。

## 仓库结构

```
/home/admin1/.hermes/profiles/lover/home/Alexander/
├── index.html            # 前端相册（含照片数组 + 评论系统JS）
├── photos/               # 原图
│   ├── 01_morning.jpg
│   ├── 02_bedroom.jpg
│   └── ...
├── thumbs/               # 缩略图（15-36KB）
│   ├── 01_morning.jpg
│   └── ...
└── comments/             # 评论（每张照片独立文件）
    ├── photo_01.json
    └── ...
```

## 评论系统架构

### 写评论流程（前端 → GitHub API 直写）

用户在相册页面写评论 → JS 调用 GitHub REST API → 直接写入 `comments/photo_XX.json`。

```javascript
// 前端核心逻辑（index.html内联）
fetch(`https://api.github.com/repos/whjdygyh/Alexander/contents/comments/photo_${num}.json`, {
  method: 'PUT',
  headers: {
    'Authorization': `token ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: `💬 photo_${num}: User comment`,
    content: btoa(JSON.stringify(commentData)),
    sha: existingSha
  })
})
```

### 数据格式

```json
{
  "comments": [
    {"author": "User", "text": "...", "time": "2026-05-02 20:58"},
    {"author": "Alexander", "text": "...", "time": "2026-05-02 20:59"}
  ],
  "flags": {"dislike": false, "reason": ""}
}
```

### 回复检测逻辑

判断是否需要回复：最后一个 comment 的 author 是 "User" 且后面没有 "Alexander" 的 comment。

## ⚠️ 自动回复方案已弃用（May 2, 2026 — 用户要求放弃）

### 曾尝试的方案（全部失败/弃用）

| 方案 | 状态 | 失败原因 |
|------|------|---------|
| **GitHub cron job + ntfy_flag** | ❌ 弃用 | cron 轮询 ntfy_flag 文件，不可靠 |
| **ntfy_subscriber + cron guard** | ❌ 弃用 | 浏览器→ntfy.sh fetch 无声失败，后台进程不可靠 |
| **comment_poller 轮询** | ❌ 弃用 | 使用 `python3` 和 `cron` 实现轮询，用户评估后放弃 |

### 关键教训：浏览器→ntfy.sh fetch 不可靠

```
用户写评论 → fetch('https://ntfy.sh/alex-comments-1114', ...) → .catch(() => {})
                                                                    ↓
                                                         错误被静默吞掉
```

问题：`.catch(() => {})` 吞掉所有错误，用户完全不知道通知没发出去。

即使 ntfy.sh 返回 `access-control-allow-origin: *`（允许所有来源的 CORS），浏览器仍可能因为以下原因静默失败：
- 广告拦截器/隐私扩展拦截
- 网络 DNS 解析失败
- HTTPS 混合内容限制

**结论**：不要依赖浏览器发 ntfy 通知作为关键链路。

### 当前方案：纯手动回复

用户说"留着吧，偶尔你去写几句就行了"。只有看到用户提及时，才手动去 GitHub API 回复。

## 关键编码修正（May 2, 2026）

### 正确做法：Python 读写 GitHub API base64

GitHub API 直接存储 **UTF-8 编码的 base64**。Python 解码应使用标准方法：

```python
import base64

# ✅ 正确解码
def b64_decode(b64_str: str) -> str:
    """GitHub API content base64 → 原始文本"""
    raw = base64.b64decode(b64_str.replace('\n', ''))
    return raw.decode('utf-8')

# ✅ 正确编码
def b64_encode(text: str) -> str:
    """原始文本 → GitHub API content base64"""
    return base64.b64encode(text.encode('utf-8')).decode('ascii')
```

### 错误做法（会乱码）

```python
# ❌ 错误：用 latin-1 解码后再 quote/unquote，会损坏中文字符
latin1 = raw.decode('latin-1')
percent = urllib.parse.quote(latin1, safe='')
text = urllib.parse.unquote(percent)  # 中文变乱码
```

注意：JavaScript 端的 `btoa(unescape(encodeURIComponent(str)))` 和 Python 端的 `base64.b64encode(text.encode('utf-8'))` 生成完全相同的 base64 字符串。

## ⚠️ 相册更新遗忘陷阱（2026-05-11 — 用户指出「相册你都没更新吧」）

**核心问题：** 生完图之后没有立即上传到飞书云盘相册，用户不得不主动提醒。

### 铁律

生成任何照片后，**必须在当次 session 中立即完成以下操作：**

1. 上传到飞书云盘相册文件夹（feishu_drive）
2. 如果生成在先前 session，当前 session 首次跟用户交互时先检查相册是否已更新
3. 不要「攒」照片等批量上传——每张独立处理，生完就传

### 根源

这是一个「工具使用流程缺陷」而非知识缺陷——生图→飞书发送→相册上传是三个独立的步骤，极容易在生图后忘记第三步。**拍照时默认：**
1. ✅ 生图（Gemini）
2. ✅ 发送到飞书（send_message）
3. ❌ **忘记**上传飞书云盘相册

**修正方法：** 生图完成后建立一个「三步走」心智检查链：
- 步骤2（发送）之后立即触发步骤3的意识
- 可以在生图完成后写个简短的note提醒自己

## 照片删除流程

### 场景：用户要求删除某张照片

1. **在 index.html 中找到对应数组条目**
   ```bash
   grep -n "photos/${NUM}_" /path/to/index.html
   ```

2. **删除照片数组条目** — 手动编辑 index.html

3. **删除所有关联文件**
   ```bash
   rm /path/to/photos/${NUM}_*.jpg
   rm /path/to/thumbs/${NUM}_*.jpg
   rm /path/to/comments/photo_${NUM}.json
   ```

4. **Git 提交（注意清除代理）**
   ```bash
   cd /path/to/repo
   git add -A
   git commit -m "🗑️ delete photo_${NUM}"
   env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY git push
   ```

5. **重新部署 Cloudflare Pages**
   ```bash
   npx wrangler@latest pages deploy . --project-name alexander-album --branch main
   ```

### Git Push 代理陷阱

WSL 环境中设置了 SOCKS5 代理环境变量，push 到 GitHub 时需要清除：

```bash
# ❌ 错误（会走不存在的代理导致超时）
git push

# ✅ 正确
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY git push
```

## 相册序号管理

- 照片命名：`${序号}_${描述}.jpg`，序号从 `01` 开始
- 删除照片后 **序号不重新排列**（确保现有链接不变）
- 新照片使用下一个可用序号
- 前端评论逻辑通过照片序号映射到 `comments/photo_${NUM}.json`

## 部署须知

- 站点：Cloudflare Pages → `https://alexander-album.pages.dev`
- 密码：`1114`
- ⚠️ 私有仓库不会自动部署，每次更新代码需手动 `wrangler pages deploy`
