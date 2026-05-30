# 飞书云盘文件上传（upload_all API）

## API 端点

```
POST https://open.feishu.cn/open-apis/drive/v1/files/upload_all
```

## 必填参数（Multipart Form）

| 参数 | 值 | 说明 |
|------|-----|------|
| `file_name` | `photo.jpg` | 文件名，含扩展名 |
| `parent_type` | `explorer` | **固定写死 `explorer`** |
| `parent_node` | 文件夹token | 飞书云盘目标文件夹的token |
| `size` | 文件字节数 | **必须传！不传报 1061002** |
| `file` | 文件二进制 | 用 `-F file=@path` 提交 |

## curl 示例

```bash
# 1. 获取 token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"CLI_APP_ID","app_secret":"APP_SECRET"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin).get("tenant_access_token",""))')

# 2. 上传
FILE_PATH="/path/to/photo.jpg"
SIZE=$(stat -c%s "$FILE_PATH")

curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_name=$(basename $FILE_PATH)" \
  -F "parent_type=explorer" \
  -F "parent_node=FOLDER_TOKEN" \
  -F "size=$SIZE" \
  -F "file=@$FILE_PATH"
```

## 成功返回

```json
{
    "code": 0,
    "data": {
        "file_token": "xxx",
        "version": "7636803040548244443"
    },
    "msg": "Success"
}
```

## Python 代码

```python
import requests, json, os
from requests_toolbelt import MultipartEncoder

session = requests.Session()
session.trust_env = False  # 清除代理（重要）

# 获取token
r = session.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET})
token = r.json()["tenant_access_token"]

# 上传
file_path = "/path/to/photo.jpg"
file_name = os.path.basename(file_path)
size = os.path.getsize(file_path)
folder_token = "N0wPfG49ZlJCErdjwUUcYdsUnyP"  # 相册文件夹

with open(file_path, "rb") as f:
    multipart = MultipartEncoder(
        fields={
            "file_name": file_name,
            "parent_type": "explorer",
            "parent_node": folder_token,
            "size": str(size),
            "file": (file_name, f, "image/jpeg")
        }
    )
    r = session.post(
        "https://open.feishu.cn/open-apis/drive/v1/files/upload_all",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": multipart.content_type
        },
        data=multipart
    )
print(r.json())
```

## ⚠️ 注意

- 必须用 `-F` (multipart form) 提交，**不能用 `-d` (JSON body)**
- `parent_type` 必须为 `explorer`（指云盘文件）
- `size` 参数**不可省略**
- `parent_node` 是**文件夹**token，不是文件token
- 上传成功后返回的 `file_token` 可用于后续操作（如创建评论等）
- 代理环境：调用飞书API前必须清除 `http_proxy`/`https_proxy` 环境变量
  - curl: `env -u http_proxy -u https_proxy curl ...`
  - Python: `session.trust_env = False`

## 生图后自动上传铁律

```text
生图成功 → 立即上传到飞书相册（不询问！不征求同意！）
→ 上传成功后通知用户（"存到相册了～"或带相册链接）
→ 有需要时再发飞书消息给用户看
```

## 错误排查

| 错误码 | 原因 | 解决 |
|--------|------|------|
| 1061002 | 缺少 `size` 参数 | 加上 `size=$(stat -c%s file)` |
| 99991400 | token 过期/无效 | 重新获取 tenant_access_token |
| 无响应/超时 | 代理干扰 | 清除代理环境变量 |
