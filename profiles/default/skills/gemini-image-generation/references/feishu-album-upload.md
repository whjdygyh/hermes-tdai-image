# Feishu Album Upload — Post-Generation Pipeline (2026-05-18 更新)

## 重大变更

**废弃了「双轨制」（飞书云盘 + 本地HTML相册/GitHub/Cloudflare Pages）。**
**现用方案：仅飞书云盘存储。**

> ❌ 停止：推送到alexander_repo仓库
> ❌ 停止：生成缩略图
> ❌ 停止：更新index.html
> ❌ 停止：Cloudflare Pages部署
> ✅ 仅做：生图 → 上传飞书云盘（drive/v1/files/upload_all）→ 发飞书消息给安迪

## Canonical Temp Path for Newly Generated Images

After Gemini image generation, ALWAYS save the output to a well-known temp path so downstream steps can find the right file:

```python
with open('/tmp/gemini_output.jpg', 'wb') as f:
    f.write(response.content)
```

**🚨 CRITICAL PITFALL — Using the wrong source file:**
- ✅ Use `/tmp/gemini_output.jpg` — the actual freshly-generated output
- ❌ Download a file from Feishu cloud drive and re-upload it — this recycles an OLD photo
- ✅ Verify: `ls -la /tmp/gemini_output.jpg` — mod time should be seconds ago

## Upload to Feishu Cloud Drive (唯一步骤)

### Determine Next File Number

List the current folder contents, extract the max numeric prefix:

```python
import re
r = requests.get(
    f"https://open.feishu.cn/open-apis/drive/v1/files?page_size=200&folder_token=N0wPfG49ZlJCErdjwUUcYdsUnyP",
    headers={"Authorization": f"Bearer {token}"}
)
files = r.json()["data"]["files"]
numbers = [int(re.match(r'(\d+)', f['name']).group(1)) for f in files if re.match(r'(\d+)', f['name'])]
next_num = max(numbers) + 1 if numbers else 1
```

### Upload API

```python
url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
headers = {"Authorization": f"Bearer {tenant_access_token}"}
file_size = os.path.getsize('/tmp/gemini_output.jpg')
data = {
    "file_name": f"{next_num}_description.jpg",
    "parent_type": "explorer",
    "parent_node": "N0wPfG49ZlJCErdjwUUcYdsUnyP",
    "size": str(file_size)
}
with open('/tmp/gemini_output.jpg', 'rb') as f:
    files = {"file": (f"{next_num}_description.jpg", f, "image/jpeg")}
    resp = requests.post(url, headers=headers, data=data, files=files)
```

**必须传 `size` 参数。不加就失败。**

### Verification (Mandatory!)

```python
r = requests.get(
    f"https://open.feishu.cn/open-apis/drive/v1/files?page_size=200&folder_token=N0wPfG49ZlJCErdjwUUcYdsUnyP",
    headers={"Authorization": f"Bearer {token}"}
)
uploaded = [f for f in r.json()["data"]["files"] if f['name'] == f"{next_num}_description.jpg"]
```

### 发飞书消息

上传到云盘**之后**，再发：

```python
# 1. Upload to message API
image_resp = requests.post(
    "https://open.feishu.cn/open-apis/im/v1/images",
    headers={"Authorization": f"Bearer {token}"},
    files={"image": open('/tmp/gemini_output.jpg', 'rb')},
    data={"image_type": "message"}
)
image_key = image_resp.json()["data"]["image_key"]

# 2. Send
requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "receive_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }
)
```

## Naming Convention

`{number}_{description}.jpg` — number = max existing + 1, description in English/pinyin lowercase.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using wrong source file | Use `/tmp/gemini_output.jpg` — verify mod time |
| Not verifying after upload | List folder contents and check |
| 忘记传size参数 | API返回200但文件未上传成功 |
| 先发飞书再传云盘 | 铁律：先云盘，再飞书 |
| 推送到GitHub | ❌废弃流程不要碰 |

## Folder Info

- **Token**: `N0wPfG49ZlJCErdjwUUcYdsUnyP`
- **URL**: https://my.feishu.cn/drive/folder/N0wPfG49ZlJCErdjwUUcYdsUnyP
