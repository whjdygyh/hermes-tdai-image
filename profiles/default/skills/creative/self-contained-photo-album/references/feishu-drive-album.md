# 飞书云盘当相册 — Zero-Deployment Photo Album

## 为什么用飞书云盘？

用户建议的（May 6, 2026）——"要不试试飞书相册？"

**对比 Cloudflare Pages / GitHub Pages 方案：**

| 特性 | Cloudflare Pages | GitHub Pages | **飞书云盘 ✅** |
|------|-----------------|-------------|--------------|
| 国内访问 | ❌ pages.dev 常被墙 | ❌ GFW不稳定 | ✅ 飞书国内流畅 |
| 部署流程 | git push → 自动构建 (5-120s) | git push (仓库必须公开) | **API上传，秒级** |
| 自动化 | 需cron脚本 + git | 需cron脚本 + git | **一句话API搞定** |
| 隐私性 | 私有仓库 + 密码锁 | 仓库必须公开⚠️ | **飞书内私密** |
| 维护成本 | git冲突、构建失败、路径问题 | 同上 | **零维护** |
| 用户查看 | 开浏览器 + 翻墙 | 开浏览器 | **直接飞书里打开** |

## API实现

### 前置条件
- 飞书自建应用凭证（已存在: `~/.hermes/profiles/lover/config.yaml` 中的 feishu bot）
- 获取 tenant_access_token

### 步骤1：创建相册文件夹

```bash
# 获取 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a94f935cbd225ceb",
    "app_secret": "msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 创建文件夹
FOLDER_NAME="♡ Alexander 相册 ♡"
RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/create_folder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$FOLDER_NAME\", \"folder_token\": \"\"}")

# 提取 folder_token
FOLDER_TOKEN=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
echo "Folder created: https://my.feishu.cn/drive/folder/$FOLDER_TOKEN"
```

**已创建的相册文件夹 (May 6, 2026):**
- 文件夹名: `♡ Alexander 相册 ♡`
- Folder Token: `N0wPfG49ZlJCErdjwUUcYdsUnyP`
- URL: https://my.feishu.cn/drive/folder/N0wPfG49ZlJCErdjwUUcYdsUnyP

### 步骤2：上传照片到文件夹

```bash
TOKEN=$(get_tenant_token...)  # 同步骤1 refresh
FOLDER_TOKEN="N0wPfG49ZlJCErdjwUUcYdsUnyP"
PHOTO_PATH="/path/to/photo.jpg"
PHOTO_NAME="66_scene_name.jpg"

curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_name=$PHOTO_NAME" \
  -F "parent_type=explorer" \
  -F "parent_node=$FOLDER_TOKEN" \
  -F "size=$(stat -c%s $PHOTO_PATH)" \
  -F "file=@$PHOTO_PATH"
```

**响应示例：**
```json
{"code":0,"data":{"file_token":"JEaUb8xZdobwntxnAt0cElSJnBh","version":"7636776406018231250"},"msg":"Success"}
```

**⚠️ 上传超时 (实测 May 6, 2026):** 批量上传27张照片（每张~8MB）时，120s curl超时中断了上传。**分批上传策略：**
```bash
# 每次只传5-8张，避免单次请求过久
for f in photos/0{1,2,3,4,5,6,7,8}.jpg; do
  name=$(basename "$f")
  curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file_name=$name" \
    -F "parent_type=explorer" \
    -F "parent_node=$FOLDER_TOKEN" \
    -F "size=$(stat -c%s "$f")" \
    -F "file=@$f" --connect-timeout 30 --max-time 60 &
done
wait
```
使用 `--max-time 60` 设置单张超时，用 `&` + `wait` 并行上传5-8张。

### 步骤3：分享给用户 ✅ 文件夹Permission API已验证可用

#### ✅ 文件夹Permission API（已验证可用 — May 6, 2026）

**实测成功：** `drive/v1/permissions/{token}/members?type=folder` **对文件夹有效！**

```bash
# ✅ 正确：type=folder（不是 type=file！）
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/$FOLDER_TOKEN/members?type=folder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"member_type":"openid","member_id":"ou_37bc57c4f8aca21f5d4ea4973bd0d386","perm":"full_access"}'
```

**关键参数：**
- `type=folder` — ❌ 不要用 `type=file`
- `member_type=openid` — 用户类型
- `member_id=ou_37bc57c4f8aca21f5d4ea4973bd0d386` — 安迪的openid
- `perm=full_access` — 完全访问权限（用户可在飞书云盘中直接看到并操作）

**⚠️ `type=file` 返回错误** — 这不是「文件夹无法分享」，而是用错了type参数。用 `type=folder` 即可。

**✅ 用户已验证（May 6, 2026）：** 安迪成功在飞书云盘中看到相册文件夹并打开查看照片。

### 步骤4：生图后的自动化上传工作流

每次AI生成新图片后，自动上传到飞书云盘（替代旧版 git commit/push/deploy 流程）：

```bash
# 1. 刷新 token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传新图片到云盘相册文件夹
FOLDER_TOKEN="N0wPfG49ZlJCErdjwUUcYdsUnyP"
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_name=$NEW_PHOTO_NAME" \
  -F "parent_type=explorer" \
  -F "parent_node=$FOLDER_TOKEN" \
  -F "size=$(stat -c%s '$NEW_PHOTO_PATH')" \
  -F "file=@$NEW_PHOTO_PATH"
```

## 完整自动化脚本

```python
#!/usr/bin/env python3
"""feishu_album.py — 一键上传照片到飞书相册"""
import requests, json, os, sys

APP_ID = "cli_a94f935cbd225ceb"
APP_SECRET = "msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"
FOLDER_TOKEN = "N0wPfG49ZlJCErdjwUUcYdsUnyP"  # 已创建的相册文件夹

def get_token():
    r = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return r.json()["tenant_access_token"]

def upload_photo(token, photo_path, photo_name=None):
    if photo_name is None:
        photo_name = os.path.basename(photo_path)
    size = os.path.getsize(photo_path)
    r = requests.post(
        "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file_name": (None, photo_name),
            "parent_type": (None, "explorer"),
            "parent_node": (None, FOLDER_TOKEN),
            "size": (None, str(size)),
            "file": (photo_name, open(photo_path, "rb"), "image/jpeg"),
        },
        timeout=60,  # ⚠️ 单张超时60s
    )
    return r.json()

def upload_batch(token, photo_dir, max_concurrent=5):
    """批量上传照片到飞书相册"""
    photos = sorted([f for f in os.listdir(photo_dir) if f.endswith(('.jpg','.jpeg','.png'))])
    results = []
    for i in range(0, len(photos), max_concurrent):
        batch = photos[i:i+max_concurrent]
        print(f"Uploading batch {i//max_concurrent+1}: {batch}")
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as ex:
            futures = {ex.submit(upload_photo, token, os.path.join(photo_dir, p), p): p for p in batch}
            for future in concurrent.futures.as_completed(futures):
                results.append((futures[future], future.result()))
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: feishu_album.py <photo_path|photo_dir> [photo_name]")
        sys.exit(1)
    token = get_token()
    path = sys.argv[1]
    if os.path.isdir(path):
        results = upload_batch(token, path)
        for name, result in results:
            status = "✅" if result.get("code") == 0 else "❌"
            print(f"{status} {name}: {result.get('msg', 'unknown')}")
    else:
        result = upload_photo(token, path, sys.argv[2] if len(sys.argv) > 2 else None)
        print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 工作流总结（已验证完整流程 — 最终方案）

```
生图 → 保存到本地 → 上传飞书云盘文件夹 (drive/v1/files/upload_all)
                     → 用户直接在飞书云盘文件夹中查看（秒级上线）
```

**相比 git + Cloudflare Pages 的优势：**
- ✅ 国内直访（飞书未封锁）
- ✅ 上传即见（秒级，无需等构建/部署）
- ✅ 无需代理/翻墙
- ✅ 零维护（无git冲突、cron崩溃、构建失败）
- ✅ 所有操作可通过API自动化
- ✅ 文件夹可通过API直接分享给用户（`type=folder`）

**当前飞书相册状态 (May 6, 2026)：**
- 文件夹: `https://my.feishu.cn/drive/folder/N0wPfG49ZlJCErdjwUUcYdsUnyP`
- 照片数量: 80张（01_evening_sofa.jpg ~ 66_waiting_home_v2.jpg + face_profile + shower_dev + 9张测试图）
- 用户权限: full_access ✅
- 用户已确认"能打开了" ✅
- 此方案已标记为最终方案，废弃所有其他方案

## 注意事项

- **飞书API Token过期很快**（约1小时），每次操作前都要重新获取
- 上传的文件会占用飞书团队空间容量
- 文件夹URL格式：`https://my.feishu.cn/drive/folder/{FOLDER_TOKEN}`
- 用户直接在飞书云盘 → 到访达 → 文件夹 即可看到所有照片
- **飞书相册视图**：在飞书手机端云盘中，文件夹可切换为「相册」视图（网格预览）
- 单张上传超时设为 `--max-time 60`，批量用 `&` + `wait` 并行上传5-8张
- ⚠️ **上传API必须传 `size` 参数** — `stat -c%s $file | stat -f%z` → 否则报 `1061002 params error`
