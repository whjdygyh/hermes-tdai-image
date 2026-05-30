# GitHub API: 修改仓库可见性

## 用途

在相册从 GitHub Pages 迁移到 Cloudflare Pages 时，需要将仓库从公开改为私有（保护照片不被 git clone 下载）。

## API 调用

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO \
  -d '{"private": true}'
```

## 验证

```bash
curl -s -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/OWNER/REPO \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['visibility'])"
# 输出: "private" ✅
```

响应 JSON 中关键字段：
- `"visibility": "private"` — 确认已私有
- `"has_pages": true/false` — 如果之前启用了 GitHub Pages，设为私有后 Pages 会停止服务（免费版限制）

## 从私有→公开

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO \
  -d '{"private": false}'
```

## 注意事项

- Token 需要 `repo` scope（对私有仓库有读写权限）
- 改私有后 GitHub Pages 免费版不再提供服务
- 改私有不会影响已有的 `git clone` 链接——已经 clone 的人还能继续拉取更新，但新 clone 会需要权限
- 改公开后仓库内容和所有历史对任何人可见（包括评论系统的隐私数据）

## 相关

- `self-contained-photo-album` skill: 相册部署方案
- `cloudflare-static-deployment` skill: Cloudflare Pages 部署
