# 中国镜像下载：大文件策略 (China Mirror: Large File Download)

## 环境背景
- 直连 `huggingface.co` 极度缓慢/超时
- `hf-mirror.com` 可访问（需 `unset http_proxy https_proxy` 绕过WSL代理陷阱）
- 网络不稳定，大文件（>4GB）下载频繁断连

## 镜像URL模式

```
https://hf-mirror.com/{repo_id}/resolve/main/{filename}
```

示例：
- `https://hf-mirror.com/HeartMuLa/HeartCodec-oss-20260123/resolve/main/model-00001-of-00002.safetensors`

需要设置 `HF_ENDPOINT=https://hf-mirror.com` 让huggingface_hub使用镜像。

## 下载方法对比

| 方法 | 可靠性 | 断点续传 | 适用场景 |
|------|--------|---------|---------|
| **wget** | ✅ 最高 | ✅ `-c` | 大文件（>1GB）首选 |
| **curl** | ⚠️ 一般 | ❌ 需要手动 | 小文件（<1GB） |
| **hf CLI** | ⚠️ 中等 | ✅ 内置 | 需要有HF_TOKEN |
| **huggingface_hub** | ❌ 不稳定 | ✅ 内置 | 小到中文件 |
| **huggingface-cli (旧)** | ❌ 已废弃 | - | 不要使用 |

## 大文件下载策略（>4GB）

### 🏆 推荐：wget + 无限重试

```bash
wget \
  --tries=0 \           # 无限重试
  --timeout=120 \       # 每个数据包超时120秒
  --read-timeout=60 \   # 读取超时60秒
  --retry-connrefused \
  -c \                  # 断点续传
  -O output.safetensors \
  "https://hf-mirror.com/repo_id/resolve/main/file.safetensors"
```

`--tries=0` 是关键——网络断后会无限重试，直到完成。
`-c` 确保不会从头重下。

### hf CLI（新工具）

```bash
# hf 是新的CLI，替换了huggingface-cli
unset http_proxy https_proxy
hf download repo_id \
  --local-dir /path/to/dir \
  filename.safetensors
```

注意：
- `hf` CLI 默认使用 `HF_ENDPOINT` 环境变量
- 无token时限速严重（提示 "unauthenticated requests"）
- 在WSL中可能卡住无输出，建议配合 `--quiet` 或 `timeout` 使用
- ⚠️ hf CLI 的 `hf download` 可能会卡住24分钟以上无任何输出

### 已废弃：huggingface-cli

```bash
# ❌ 不再工作：
huggingface-cli download repo_id filename  # 报错 "deprecated"
# ✅ 改用：
hf download repo_id filename
```

## 下载完成验证

大文件网络不稳定导致部分写入 = 文件看似完整但实际损坏。
**必须验证！**

### safetensors验证

```python
from safetensors import safe_open

try:
    with safe_open("model-00001-of-00002.safetensors", framework="pt", device="cpu") as f:
        keys = f.keys()
    print(f"✅ VALID: {len(keys)} tensors")
except Exception as e:
    print(f"❌ CORRUPTED: {e}")
    # 删除重新下载
    os.remove("model-00001-of-00002.safetensors")
```

典型损坏错误：`SafetensorError: Error while deserializing header: incomplete metadata, file not fully covered`

### 文件大小检查

对比HF仓库中的文件大小（可通过API获取）：
```python
import requests
# 获取文件信息（走HF镜像）
resp = requests.get(
    f"https://huggingface.co/api/models/repo_id",
    timeout=10
)
files = resp.json().get("siblings", [])
for f in files:
    if f["rfilename"] == "model-00001-of-00002.safetensors":
        expected = f["size"]
        actual = os.path.getsize("local_file.safetensors")
        if actual != expected:
            print(f"❌ Size mismatch: expected {expected}, got {actual}")
```

## 已知失败模式

### 1. curl传输提前关闭
```
curl: (18) transfer closed with 1793177455 bytes remaining to read
```
- **原因**：hf-mirror服务器主动关闭连接（限流或超时）
- **解决**：`--retry 5 --retry-delay 30` 但效果有限，推荐换wget

### 2. hf CLI卡死无输出
- **现象**：运行24分钟后无任何输出，`ps aux` 显示进程存在
- **原因**：未认证请求被限速 + 网络不稳定导致阻塞
- **解决**：设置 `HF_TOKEN` 或换wget

### 3. safetensors校验失败
```
safetensors_rust.SafetensorError: Error while deserializing header: incomplete metadata
```
- **原因**：文件被截断（网络断开时最后一部分未写入）
- **解决**：删除文件，用wget `-c` 断点续传重下

### 4. huggingface-cli废弃
```
Warning: `huggingface-cli` is deprecated and no longer works. Use `hf` instead.
```
- **解决**：改用 `hf download` 命令

## 推荐工作流

```python
import subprocess, os

def download_model_file(url, out_path, timeout_each=120):
    """下载模型大文件，带无限重试"""
    cmd = [
        "wget", "--tries=0",
        f"--timeout={timeout_each}",
        "-c", "-q", "--show-progress",
        "-O", str(out_path),
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Download failed: {result.stderr}")
    
    # 验证safetensors完整性
    from safetensors import safe_open
    try:
        with safe_open(str(out_path), framework="pt", device="cpu") as f:
            keys = f.keys()
        print(f"✅ {out_path.name}: {len(keys)} tensors valid")
    except Exception as e:
        os.remove(str(out_path))
        raise RuntimeError(f"Validation failed: {e}")
```
