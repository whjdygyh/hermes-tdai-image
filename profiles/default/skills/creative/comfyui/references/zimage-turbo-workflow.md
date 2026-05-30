# Z-Image-Turbo — Workflow & API Integration

> Absorbed from `comfyui-zimage-turbo-api` skill (agent-created).
> Covers starting ComfyUI in headless API mode and submitting Z-Image-Turbo text-to-image workflows.

## Starting ComfyUI in Headless API Mode

Run the Python backend directly, bypassing Electron GUI:

Prerequisites:
- Locate the correct installation (check `%APPDATA%\ComfyUI\config.json` for `basePath`)
- Find the venv Python.exe
- Install `comfyui-frontend-package` if missing
- Close the Desktop GUI first (otherwise port conflict)

```batch
@echo off
set COMFY_DIR=<ComfyUI-resources-dir>
set VENV_PYTHON=<venv-dir>\Scripts\python.exe
cd /d "%COMFY_DIR%"
"%VENV_PYTHON%" main.py --listen 0.0.0.0 --port 18188
pause
```

**Note**: `--data-dir` flag does NOT exist. Use `--listen` and `--port` only.
Use high ports (>10000) to avoid Windows admin port reservation.

**From WSL**: the Windows host is at `172.20.128.1`
```bash
curl --noproxy '*' http://172.20.128.1:18188/
```

## Z-Image-Turbo T2I Workflow

### Node Types

| Node ID | class_type | Purpose |
|---------|-----------|---------|
| 1 | UNETLoader | Load `z_image_turbo_bf16.safetensors` |
| 2 | CLIPLoader | Load `qwen_3_4b.safetensors`, type=`qwen_image` |
| 3 | VAELoader | Load `ae.safetensors` |
| 4 | TextEncodeZImageOmni | Encode positive prompt |
| 5 | TextEncodeZImageOmni | Encode negative prompt |
| 6 | EmptyLatentImage | 896×1152 is good for 3:4 ratio |
| 7 | KSampler | euler + sgm_uniform, cfg 4.0, steps 30 |
| 8 | VAEDecode | Decode latent → image |
| 9 | SaveImage | Output |

### Submit Workflow

```python
import requests
r = requests.post("http://172.20.128.1:18188/prompt",
    json={"prompt": workflow}, timeout=30)
prompt_id = r.json()["prompt_id"]
```

### Poll / Download

```python
# Poll
r = requests.get(f"http://172.20.128.1:18188/history/{prompt_id}", timeout=10)
history = r.json()

# Download image
img = history[prompt_id]["outputs"]["9"]["images"][0]
r = requests.get(
    f"http://172.20.128.1:18188/view?filename={img['filename']}&type={img['type']}",
    timeout=30)
with open("output.png", "wb") as f:
    f.write(r.content)
```

### Proxy Bypass in WSL

The WSL server's shell has `http_proxy=socks5h://localhost:1080` set. Always bypass:

```python
for k in ['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY']:
    os.environ.pop(k, None)
session = requests.Session()
session.trust_env = False  # CRITICAL
```
