# ComfyUI Electron Desktop — Windows Troubleshooting

> Absorbed from `comfyui-electron-troubleshooting` skill (agent-created).
> Covers ComfyUI Electron Desktop app issues on Windows: base path relocation, ToDesktop updates, venv/PyTorch problems.

## Base Path Configuration

**Problem**: After moving ComfyUI to a different drive (e.g., G:→C:), the `basePath` in config is stale.

**Fix**: Update `%APPDATA%\ComfyUI\config.json` (`"basePath"`) and `%APPDATA%\ComfyUI\extra_models_config.yaml` (`"base_path"`). Both must point to the same writable data directory (NOT inside Program Files).

**Pitfall**: Paths with spaces in extra_models_config.yaml need double backslashes: `G:\\ComfyUI_Data`

> Note: If the user also clicks the "Select" button and browses via the ComfyUI dialog, it auto-rewrites config.json. Do both approaches (edit + dialog), not either-or.

## Python / venv / PyTorch CUDA Problems

**Problem**: `Torch not compiled with CUDA enabled` — the venv has CPU-only PyTorch.

**Root cause — uv cache poisoning**: On first venv creation, `--extra-index-url` may fail → uv downloads CPU torch from PyPI → caches it. Deleting + recreating venv still gets CPU torch because uv reuses cache.

**Fix — clear uv cache first**, then recreate venv with `--index-strategy unsafe-best-match`:

```batch
@echo off
"<COMFY_INSTALL_DIR>\\resources\\uv\\win\\uv.exe" cache clean
rmdir /S /Q "<BASE_PATH>\\.venv" 2>nul
"<COMFY_INSTALL_DIR>\\resources\\uv\\win\\uv.exe" venv "<BASE_PATH>\\.venv" --python 3.12
"<BASE_PATH>\\.venv\\Scripts\\uv.exe" pip install torch==2.11.0+cu130 torchvision==0.26.0+cu130 torchaudio==2.11.0+cu130 --extra-index-url https://download.pytorch.org/whl/cu130 --index-strategy unsafe-best-match
```

**Key**: `--index-strategy unsafe-best-match` is mandatory — without it, uv prefers PyPI's CPU torch.

## ToDesktop Update Conflicts

ComfyUI Electron uses ToDesktop auto-updater which installs to `%LOCALAPPDATA%\Programs\ComfyUI\`. When an update is accepted, it installs to C drive even if the app was on G drive.

**Recommended strategy**: Accept C drive install for the program (small, ~525MB), keep model data on G drive via `config.json` basePath. This avoids fighting ToDesktop's auto-update cycle.

## Port Binding Errors

- Low ports (8188-8190) may fail with `[winerror 10013]` due to Windows admin port reservation
- **Fix**: Use high ports (`--port 18188`)
- Connection from WSL: accessible at WSL default gateway IP (`172.20.128.1`)

## Frontend Package Missing

ComfyUI 0.19+ split frontend into `comfyui-frontend-package`. Install with:
```batch
"%VENV_PYTHON%" -m pip install comfyui-frontend-package
```

## Config File Locations

- `%APPDATA%\ComfyUI\config.json` — user config (basePath, GPU selection)
- `%APPDATA%\ComfyUI\extra_models_config.yaml` — extra model paths
- `{install_dir}\resources\override.txt` — PyTorch version overrides

## WSL-to-Windows Operations

- **cmd.exe** can't run from WSL UNC paths — write .bat to `/mnt/c/Users/<user>/AppData/Local/Temp/` and execute via `/mnt/c/Windows/System32/cmd.exe /c`
- **.bat files from WSL** need CRLF line endings: `sed -i 's/$/\r/' file.bat`
- **Chinese characters in PowerShell scripts** from WSL cause encoding errors — use only ASCII/English
- **Proxy env vars** in WSL break `curl` → use `--noproxy '*'`
