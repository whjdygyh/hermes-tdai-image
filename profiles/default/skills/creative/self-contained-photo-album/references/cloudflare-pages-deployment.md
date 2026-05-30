# Cloudflare Pages 部署方案

## 为什么选择 Cloudflare Pages（May 2026）

### 场景A：从 Netlify 迁移（带宽超标）

| 特性 | Netlify 免费版 | Cloudflare Pages 免费版 |
|------|---------------|------------------------|
| **带宽** | **100GB/月**（实测用完即 503） | **无限制**（官方文档未列任何带宽上限） |
| 文件数 | 不限 | 20,000 个/站点 |
| 单文件大小 | 8MB（部署限制） | 25 MiB |
| 构建次数 | 300分钟/月 | 500次/月 |
| 自定义域名 | 支持 | 支持（100个/项目） |
| 私有仓库 | ✅ 支持 Git 自动部署 | ✅ 支持 Git 自动部署 |

**结论：** 对于照片相册（每月可能消耗数 GB~数十 GB 流量），Cloudflare Pages 免费计划才是真正的无限流量方案。

### 场景B：从 GitHub Pages 迁移（隐私保护）

| 特性 | GitHub Pages 免费版 | Cloudflare Pages 免费版 |
|------|--------------------|------------------------|
| **仓库可见性** | **必须公开** 🚫 — 任何人可 git clone 所有照片+评论 | **支持私有** ✅ — 只有仓库协作者能访问 |
| 带宽 | 100GB/月 | 无限制 |
| 部署方式 | `git push` 自动部署 ✅ | `git push` 自动部署 ✅ |
| 密码保护 | 前端 JS 密码锁（`1114`） | 前端 JS 密码锁（无需改动） |
| 评论系统 | GitHub API（带 token） | GitHub API（带 token，对私有仓库同样有效） |

**结论：** 如果隐私是第一优先级（不希望任何人 git clone 照片），Cloudflare Pages 是唯一免费且支持私有仓库的部署方案。

## 部署步骤

### 先决条件

1. Cloudflare 账号（用 Google 登录即可：https://dash.cloudflare.com/sign-up）
2. GitHub 仓库已准备好（whjdygyh/Alexander）

### 步骤 1：安装 Cloudflare GitHub App

首次部署时 Cloudflare 会引导安装 GitHub App。

1. 登录 Cloudflare Dashboard → **Workers & Pages**
2. 点 **Create application** → **Pages** → **Connect to Git**
3. 如果是首次，会显示「Connect GitHub」按钮 → 点它 → 跳转到 GitHub 授权页
4. 授权时会要求选择仓库：选 **whjdygyh/Alexander**
5. 点击 **Install & Authorize**

### 步骤 2：仓库选择（刷新问题）

**常见陷阱：** 安装完 GitHub App 后返回 Cloudflare 页面，可能仍然显示「Connect GitHub」按钮，不显示仓库列表。

**修复方法：**
- **F5/Command+R 刷新页面**（硬刷新）
- 可能需要完全关闭该标签页后重新打开 Cloudflare Workers & Pages 页面
- 如果仍不行：GitHub 侧确认 App 已安装（Settings → Applications → Cloudflare Workers and Pages 状态为 Installed）

### 步骤 3：配置项目

1. 选择仓库 **whjdygyh/Alexander**
2. **Project name:** 自动生成（如 `alexander`），可用默认值
3. **Production branch:** `main`
4. **Build command:** 留空（纯静态 HTML，无构建步骤）
5. **Build output directory:** `/`（或留空）
6. 点 **Save and Deploy**

构建完成后会获得一个 `*.pages.dev` 域名，例如 `alexander-xxx.pages.dev`。

### 步骤 4：验证

```bash
curl -sI https://your-project.pages.dev/ | head -5
# 应返回 HTTP/2 200
```

## 后续更新

与 Netlify 一样：`git push` → Cloudflare 自动检测 → 自动构建和部署。

```bash
cd /home/admin1/alexander_repo
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
git add -A
git commit -m "📸 update"
git push
```

等待约 1-2 分钟部署完成。

## 从 Netlify 迁移

1. 在 Cloudflare Pages 创建项目（步骤 1-3）
2. Netlify 站点删除（可选）：Netlify Dashboard → Site settings → Delete site
3. 通知用户新域名
4. 评论系统的 JSON 文件自动跟随 git 仓库，无需额外迁移

## 从 GitHub Pages 迁移（代码变更）

**仅需改动 `<base>` 标签一处代码：**

```diff
- <base href="/REPO_NAME/">  <!-- GitHub Pages 路径 -->
+ <base href="/">             <!-- Cloudflare Pages 路径 -->
```

所有其他路径（`photos/`、`thumbs/`、`comments/`）不需要动。

### ⚠️ 密码检查陷阱

迁移时必须确认密码未被调试过程误改为 `***`：

```bash
curl -s "https://new-site.pages.dev/" | grep CORRECT_PASSWORD
# 如果返回 CORRECT_PASSWORD="***"，需在 index.html 中改回 1114
```

### 用户操作步骤

1. **GitHub 侧：** 仓库 Settings → Danger Zone → 设为 Private
2. **Cloudflare 侧：** Dashboard → Pages → Connect to Git → 选择私有仓库 → 部署
3. **旧域名：** GitHub Pages 自动失效（私有仓库不再提供 Pages 服务）
4. **新域名：** 告知用户 Cloudflare 分配的 `*.pages.dev` 域名

### 无需改动

- ✅ 密码（`1114` 不变）
- ✅ 评论系统（GitHub API 对私有仓库同样工作，token 不变）
- ✅ 自动回复系统（ntfy_subscriber.py 监听评论，不受影响）
- ✅ 照片文件路径（`photos/` + `thumbs/` 不变）

## 已知限制

- 免费计划 500 次构建/月 — 我们的更新频率远低于此
- 如果使用 Pages Functions（用不到，纯静态），将按 Workers 计费
- 免费版不支持自定义域名的 HTTPS（但 `*.pages.dev` 子域名自带 HTTPS）
