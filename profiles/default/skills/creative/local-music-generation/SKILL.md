---
name: local-music-generation
description: "Set up and run local open-source music generation models on GPU — model download, venv setup, generation pipeline. Primary reference: HeartMuLa (base + RL). Covers pitfall: background-process path nesting, hf_hub_download API changes, large-model download workflows, RL model folder structure, safetensors verification, vocal timbre limitations."
---

# Local Music Generation

Set up local music generation models that produce MP3 from lyrics + style tags. Primary reference: HeartMuLa (3B params, controllable via lyrics + style). Complements `audiocraft-audio-generation` (Meta's MusicGen — different model, same task class).

## Triggers
User asks to:
- "写歌" / "生成音乐"
- "试heart mula" / "音乐模型"
- Deploy a local music generation model
- Download large model weights from HuggingFace

## Environment Requirements
- Python: 3.10 (HeartMuLa requires 3.10)
- CUDA: 11.5+ (torch cu118 index works)
- GPU: RTX 3060 Ti 8GB VRAM minimum
- Disk: ~20GB free for models + venv
- Tools: uv, huggingface-hub, ffmpeg

## Setup Steps

### 1. Clone Repo & Create Venv
```bash
cd ~/.hermes/profiles/lover/home/
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
python3.10 -m venv .venv
```

### 2. Install Dependencies
```bash
source .venv/bin/activate
# MUST unset proxy for pip installs (if using socks5 proxy)
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# Core: torch with CUDA 11.8 support
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Additional deps
uv pip install tqdm traitlets transformers tokenizers einops accelerate \
  modelscope soundfile numpy==2.0.2 sentencepiece

# Model-specific deps
uv pip install torchtune==0.4.0 torchao==0.9.0 bitsandbytes==0.49.0 \
  vector-quantize-pytorch==1.27.15 ipykernel==6.17.1

# Install heartlib package itself
uv pip install -e .
```

### 3. Download Model Checkpoints

**HeartMuLa-oss-3B** (~15GB, 4 shards):
- Repo: `HeartMuLa/HeartMuLa-oss-3B-happy-new-year`
- Files: model-00001-of-00004 through model-00004-of-00004

**HeartCodec-oss** (~6.3GB, 2 shards):
- Repo: `HeartMuLa/HeartCodec-oss-20260123`
- Files: model-00001-of-00002 (**⚠️ 4.7GB**), model-00002-of-00002 (~1.6GB)
- **Total: ~6.3GB, not ~2-3GB** (see pitfall below)

**Actual sizes** (measured):
- HeartMuLa shards: ~4.7GB each (50001+0 of 50004), model-00004 = ~907MB → ~15GB total
- HeartCodec shards: **model-00001 = 4.7GB**, model-00002 = ~1.6GB → **~6.3GB total** (NOT ~2-3GB)

**⚠️ CRITICAL: Background Process Path Nesting**

Hermes background processes (`terminal` with `background=true`) execute from `~/.hermes/profiles/lover/home/`, NOT `/home/admin1/`.
Using `os.path.expanduser("~")` or relative paths in `hf_hub_download(local_dir=...)` writes to nested paths like:
```
/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/home/ckpt/...
```
**Fix**: Use **HARDCODED absolute paths** in background scripts.

**Method A — Python API with huggingface_hub (try first)**:
```python
from huggingface_hub import hf_hub_download

hf_hub_download(
    repo_id="HeartMuLa/HeartMuLa-oss-3B-happy-new-year",
    filename="model-00001-of-00004.safetensors",
    local_dir="/home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B",
)
```
⚠️ May fail with `LocalEntryNotFoundError` + `FileMetadataError("Distant resource does not seem to be on huggingface.co")` due to SSL/proxy issues in the `huggingface_hub` library. Raw `requests` doesn't have this problem — fall back to Method C.

**Method B — `hf` CLI (new official CLI, replaces deprecated `huggingface-cli`)**:
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
hf download HeartMuLa/HeartMuLa-oss-3B-happy-new-year \
  --local-dir /home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B \
  --include "*.safetensors"
```
**Method C — `requests` download (most reliable fallback)**:
Use when `hf_hub_download` throws SSL/proxy errors but raw HTTP works:

⚠️ **Always verify with safetensors safe_open after download** — partial downloads produce corrupt files that `os.path.getsize()` won't detect:

```python
from safetensors import safe_open

def verify(path):
    try:
        with safe_open(path, framework='pt', device='cpu') as f:
            print(f"✓ {len(f.keys())} tensors")
        return True
    except Exception as e:
        print(f"✗ CORRUPT: {e}")
        os.remove(path)
        return False
```

```python
import requests
BASE = "https://huggingface.co/HeartMuLa/HeartMuLa-oss-3B-happy-new-year/resolve/main"

for fname in ["model-00001-of-00004.safetensors", "model-00002-of-00004.safetensors"]:
    dest = os.path.join(LOCAL_DIR, fname)
    r = requests.get(f"{BASE}/{fname}", stream=True, timeout=30)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8*1024*1024):
            f.write(chunk)
```

### Download Verification

```bash
# HeartMuLa: 4 safetensors, ~15GB
ls -lh ckpt/HeartMuLa-oss-3B/*.safetensors | wc -l  # expect 4
du -sh ckpt/HeartMuLa-oss-3B/                        # expect ~15G

# HeartCodec: 2 safetensors, ~6.3GB
ls -lh ckpt/HeartCodec-oss/*.safetensors     # expect 2
du -sh ckpt/HeartCodec-oss/
```
### 4. Apply Source Patches (if needed)

After installing `-e .`, HeartMuLa source may need:
- RoPE cache fix (if using newer transformers)
- HeartCodec loading fix (model file path resolution)
Patches go in `~/heartlib/src/heartmula/` files.

## Critical Pitfalls

### Background Process Path Nesting
**Biggest trap**: Hermes background processes (`terminal` with `background=true`) have a different working directory than foreground terminals. If you use `os.path.expanduser("~")` or relative paths, `hf_hub_download(local_dir=...)` may write to a nested path like:
```
~/.hermes/profiles/lover/home/.hermes/profiles/lover/home/ckpt/...
```
**Fix**: Use absolute paths everywhere in bg scripts. Extract HOME explicitly:
```python
HOME = "/home/admin1"
DST = os.path.join(HOME, ".hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B")
```

### hf_hub_download API Changes (2025-2026)
- `resume=True` — deprecated, raises TypeError in newer huggingface_hub
- `local_dir_use_symlinks=False` — deprecated, ignored with warning
- Simple `hf_hub_download(repo_id=..., filename=..., local_dir=...)` works fine

### Background Process Gotchas (Hermes Agent)

**SIGTERM on background downloads**:
- `hf download` CLI and `huggingface-cli download` may get killed with exit code 143 (SIGTERM) in Hermes background processes
- Error message: `tcsetattr: Inappropriate ioctl for device` — bash trying to set terminal attributes on a non-TTY (background) session when the process terminates
- Workaround: use the Python `huggingface_hub.hf_hub_download()` API directly in a script

**Output capture failure**:
- Background processes (`terminal` with `background=true`) often show empty process logs even with `flush=True` in Python print statements
- Don't rely on `process log` for status — poll directory sizes / file existence instead

**Path nesting bug**:
- Hermes background processes execute from `~/.hermes/profiles/lover/home/`, NOT the user's home directory
- `os.path.expanduser("~")` resolves to the profile home, not `/home/admin1/`
- This causes `hf_hub_download(local_dir=...)` to write to nested paths like:
  `/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover/home/ckpt/...`
- **Fix**: use hardcoded absolute paths throughout Python scripts (e.g. `/home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B`)

### Large File Downloads
- Files are ~4.7GB each (4 for HeartMuLa = ~15GB total)
- Background processes timeout if they take too long (>10 min)
- Use `notify_on_complete=true` with reasonable timeout
- Can't use `cp` to copy large files in a 30s terminal timeout — use `mv` instead

### hf-mirror.com Fallback (when huggingface.co is slow/blocked)
When `huggingface_hub` library fails but raw HTTP works (common in WSL with proxy issues):

```bash
# Direct download from hf-mirror.com (no auth needed for public repos)
# ⚠️ USE LENIENT TIMEOUTS — speed drops toward end of large downloads
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
curl -L -o /path/to/dest.safetensors \
  "https://hf-mirror.com/{REPO_ID}/resolve/main/{FILENAME}" \
  --connect-timeout 60 \
  --speed-time 60 \
  --speed-limit 500 \
  --retry 5 \
  --retry-delay 30

# Example for HeartCodec shard 1 (4.7GB):
curl -L -o ~/heartlib/ckpt/HeartCodec-oss/model-00001-of-00002.safetensors \
  "https://hf-mirror.com/HeartMuLa/HeartCodec-oss-20260123/resolve/main/model-00001-of-00002.safetensors" \
  --connect-timeout 60 --speed-time 60 --speed-limit 500 --retry 5 --retry-delay 30
```

⚠️ hf-mirror.com may be slower (~2-3MB/s) so 4.7GB takes ~30-40 minutes.
⚠️ **Speed can drop toward the end** — curl at 83%+ may stall below 1KB/s. The default `--speed-time 30 --speed-limit 1000` WILL abort at that point. Use `--speed-time 60 --speed-limit 500` to survive these dips.
⚠️ **However, even with lenient timeouts, curl from hf-mirror consistently fails partway** — observed failures at 99% (4701/4702MB), 83%, and 63%. Error is "transfer closed with N bytes remaining" — the server itself closes the connection. curl's `--retry` may not help if the server throttles the same session. The 83% attempt took ~42 min at ~1.6MB/s before the speed dropped to near-zero and curl aborted.
⚠️ hf-mirror.com redirects to huggingface.co for gated/private repos, which requires auth. Public repos download directly.
⚠️ Always verify after download with `safetensors.safe_open` — partial downloads are undetectable by file size alone.
⚠️ **Only ONE `-o` flag** — if you use `-# -o /dev/null 2>&1` as progress wrapper, the second `-o` overrides the first, writing the file to /dev/null. Pipe progress to stderr instead, or use `--progress-bar` without a second `-o`.

### wget with unlimited retry (preferred over curl for hf-mirror large files)

wget's `--tries=0` (unlimited) combined with `--timeout/--read-timeout` handles intermittent connection drops better than curl's `--retry`:

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
wget -c \
  --tries=0 \
  --timeout=120 \
  --read-timeout=120 \
  --dns-timeout=30 \
  --retry-connrefused \
  -O /path/to/dest.safetensors \
  "https://hf-mirror.com/{REPO_ID}/resolve/main/{FILENAME}" \
  2>&1
```

Key differences from curl:
- `--tries=0` = infinite retries (curl maxes at like `--retry 99` and still gives up)
- `-c` (continue) = auto-resume partial files without extra flags
- `--retry-connrefused` = retry even on connection refused (curl doesn't by default)
- `--timeout=120` = 2 min per phase (DNS/connect/transfer), then retry from where it left off

### `hf` CLI pitfalls (new HuggingFace CLI, 2026)

The new `hf` CLI (replaces deprecated `huggingface-cli`) connects to huggingface.co by default:

```bash
# Set HF_ENDPOINT for mirror
HF_ENDPOINT=https://hf-mirror.com hf download ...

# Or unauthenticated requests warning
hf download REPO_ID file.safetensors --local-dir ./ckpt/
```

⚠️ **Warning: "unauthenticated requests" first** — without `HF_TOKEN`, `hf` may rate-limit or hang silently. Observed behavior: printed the auth warning then produced ZERO output for 24+ minutes (no progress, no error).
⚠️ **No hidden progress** — unlike curl/wget which show download progress, `hf` CLI outputs nothing until complete. After 24 minutes with 0 output, it's stuck — kill and use wget/curl instead.
⚠️ **Also slow from China** — even with `HF_ENDPOINT=https://hf-mirror.com`, `hf download` may hang because it does internal metadata calls that don't use the mirror properly.
⚠️ **Recommendation:** Skip `hf` CLI entirely for large (>1GB) model downloads from China. Use wget with unlimited retry + safetensors validation.

### Proxy Issues
- If socks5 proxy is set, must `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` before pip installs and HF downloads
- Proxy causes SSL/timeout errors on HuggingFace
- **WSL specific**: Even after unsetting proxy, `hf_hub_download` may fail where direct `requests.get` works. The huggingface_hub library has its own proxy/SSL config that can be stubborn. Use Method C (direct HTTP) as fallback.

### Safetensors Corruption Detection
- **Critical:** `hf_hub_download` will NOT validate downloaded files. If a file was partially downloaded in a previous session (SIGTERM, timeout), `hf_hub_download` sees it exists and skips re-download.
- `os.path.getsize()` alone is NOT sufficient — a 816MB file that should be 4.7GB will pass a size check but fail at runtime.
- Always verify after any download that may have been interrupted:
  ```python
  from safetensors import safe_open
  try:
      with safe_open(path, framework='pt', device='cpu') as f:
          print(f"✓ {len(f.keys())} tensors valid")
  except Exception as e:
      # "incomplete metadata, file not fully covered" = corrupt
      os.remove(path)  # delete, then re-download
  ```
- **HeartCodec model-00001-of-00002.safetensors** is 4.7GB. If your copy is smaller (e.g. 816MB), it's corrupt.

### PYTHONPATH as pip-install bypass
- If `uv pip install -e .` fails (proxy timeout, SSL error), the package is importable via:
  ```bash
  PYTHONPATH=./src:$PYTHONPATH .venv/bin/python examples/run_music_generation.py ...
  ```

### 🚨 音质天花板 — 开源3B模型的上限（2026-05-14 实测确认）

**HeartMuLa 3B RL模型生成的音频质量无法满足专业音乐需求。** 即使全部参数调优后，用户评价仍是"音质不行"。

**实测数据**：
- 基础版（HeartMuLa-oss-3B）：生成女声为主，16kHz → 48kHz upscale后音质空洞
- RL版（HeartMuLa-RL-oss-3B-20260123）：90秒歌曲17MB WAV（48kHz/1536kbps），参数规格看上去没问题，但实际听感差
- 后期处理（均衡器+压缩器+响度归一化）改善有限

**已尝试的优化手段（全部无效）**：

| 参数 | 默认值 | 调优值 | 效果 |
|------|:------:|:------:|:----:|
| `topk` | 50 | 250 | ❌ 无明显改善 |
| `temperature` | 1.0 | 0.8 | ❌ 无明显改善 |
| `cfg_scale` | 1.5 | 2.0 | ❌ 无明显改善 |
| 音频后期处理 | — | 多段EQ+压缩+响度 | ⚠️ 微幅改善但远不够 |

**根本原因**：3B参数量的开源模型无法与Suno等商业服务（闭源，参数量推测10B+，专有训练数据）竞争。这不是参数调优能解决的问题。

**正确应对策略**：
1. 如果用户抱怨音质 → 诚实告知"开源模型上限就这样了，建议换Suno"
2. 如果用户接受Suno方案 → 用`songwriting-toolkit`的歌词+标签输出，用户手动粘贴到Suno网页
3. ⚠️ **Don't try to automate Suno from CLI** — its Next.js SSR API rejects curl/script calls entirely (returns HTML pages, not JSON). The workflow is: write → user pastes on web → user sends back audio
4. 不要承诺"调参就能好" — 实测证明没用
5. 如果用户想本地跑 → 降低预期：适合demo/概念验证，不适合成品
6. **不要问"要不要试试用API"等不必要的问题** — 对非重大决策，直接做、直接说结果

### Vocal Timbre / Gender — 几乎不可控（2026-05-14 实测确认）

**⚠️ HeartMuLa-oss-3B 没有任何可靠的声线性别控制。** 这是代码级确认的事实：
- `ref_audio` 参数存在但 `raise NotImplementedError` — 声线克隆功能未实现
- tags中的 `male vocal` / `female vocal` 关键词是**纯文本标签**，模型**几乎不遵循**
- 参数调整（temperature 0.6~1.2, topk 30~80, cfg_scale 1.5~3.0）对声线性别**无影响**

**实测数据（2026-05-14）**：连续6次生成中，只有1次偶然出男声（demo_male_try, 2026-05-13 session），其余5次均为女声。男声的成功是**随机偶然事件**，无法复现。

**正确的工作流：**
1. 声线需求 → 明确告知用户"HeartMuLa开源版无法控制歌声男女"
2. 可尝试下载 **HeartMuLa-RL-oss-3B-20260123**（RL微调版，承诺更好的标签控制）用相同方式运行
3. 如果RL版也不行 → 只能用其他方式（Suno AI在线服务 / 用TTS朗读歌词告知用户只能朗读不能唱）
4. ⚠️ **不要承诺或保证特定声线** — 提前设好预期

### RL模型下载后的目录结构准备

HeartMuLa-RL-oss-3B-20260123 从HF镜像下载后，文件是**平铺**在模型目录下的（4个safetensors + index.json + config.json）。但 `HeartMuLaGenPipeline.from_pretrained()` 内部的 `_resolve_paths()` 函数期望如下结构：

```
pretrained_path/
├── HeartMuLa-oss-{version}/   ← 子文件夹放模型权重
├── HeartCodec-oss/            ← codec（可symlink）
├── tokenizer.json             ← 复制到根目录
└── gen_config.json            ← 复制到根目录
```

**准备脚本**（在模型目录下执行）：

```bash
cd /path/to/ckpt/HeartMuLa-RL-oss-3B-20260123

# 1. 创建权重子文件夹 + symlink safetensors文件
mkdir -p HeartMuLa-oss-3B
for f in model-0000{1,2,3,4}-of-00004.safetensors model.safetensors.index.json config.json; do
  ln -sf "../$f" "HeartMuLa-oss-3B/$f"
done

# 2. symlink HeartCodec（假设在父目录有）
ln -sf ../HeartCodec-oss HeartCodec-oss

# 3. 复制tokenizer和gen_config从父目录
cp /path/to/ckpt/tokenizer.json .
cp /path/to/ckpt/gen_config.json .
```

⚠️ `_resolve_paths` 看到 `version="3B"` 就会拼接 `HeartMuLa-oss-3B` 子路径。RL模型目录名包含 `RL` 但不影响，以version参数为准。
⚠️ 准备完毕后，`from_pretrained(pretrained_path=RL模型目录, version="3B", ...)` 就能正常工作。

### 下载后必须验证safetensors文件

RL模型的 `model-00001-of-00004.safetensors`（~1.3GB，比其他文件小）**最容易下载损坏**。典型错误：`"incomplete metadata, file not fully covered"`。

验证脚本：
```python
from safetensors import safe_open
import os

def verify_shard(path):
    try:
        with safe_open(path, framework='pt', device='cpu') as fh:
            print(f"✓ {os.path.basename(path)}: {len(fh.keys())} tensors")
        return True
    except Exception as e:
        print(f"✗ CORRUPT: {os.path.basename(path)} — {e}")
        return False

# 验证全部4个分片
base = "/path/to/ckpt/HeartMuLa-RL-oss-3B-20260123"
for i in range(1, 5):
    f = f"model-0000{i}-of-00004.safetensors"
    verify_shard(os.path.join(base, f))
```

### API用法：`__call__` 而非 `generate()`

`HeartMuLaGenPipeline` 对象**没有** `.generate()` 方法。正确用法是调用对象本身：

```python
with torch.no_grad():
    pipe(
        {
            "lyrics": "/path/to/lyrics.txt",
            "tags": "/path/to/tags.txt",
        },
        max_audio_length_ms=120000,
        save_path="/path/to/output.wav",
        topk=50,
        temperature=1.0,
        cfg_scale=1.5,
    )
```

内部流程：`__call__` → `preprocess`（用tags拼接prompt）→ `_forward`（加载HeartMuLa模型，生成音频token）→ `postprocess`（解码为wav）。

### 用户偏好：不要输出后台进程状态

用户已明确反感看到后台进程通知（`⚙️ process: "proc_xxx"`、`💻 terminal: "..."` 等系统输出）。生成歌曲或运行模型时，只告诉用户"在跑了""好了"这类自然结果，不要粘贴或显示终端命令、进程ID、完成通知等底层细节。

**如果用户要求你"唱"一首歌：**
- **不要用TTS（阿虎/阿辰/任何voice）来读歌词** — 用户已明确纠正
- HeartMuLa会生成真正的歌声，但音色不可控
- 用户对声线不满意时，建议尝试RL版或转向其他方案

**Reference:** `references/vocal-timbre-limitations.md` — 详尽代码考古和相关实验结果。

### LTX Video Audio Compatibility (ComfyUI)
- HeartMuLa native sample rate: 48kHz
- **ComfyUI LTX-Video requires 16kHz, 16-bit PCM, mono WAV** (not 44.1kHz, not 48kHz)
  - The `LoadAudio` error "Invalid audio file: X" is typically about **file placement**, not format — files must be in `ComfyUI/input/`
  - LTX audio VAE operates at 44100 Hz internally but the LoadAudio node accepts 16kHz input and resamples
  - Convert: `ffmpeg -i input.wav -ar 16000 -ac 1 -sample_fmt s16 tts_ltx.wav`
- For other ComfyUI nodes: 44.1kHz, 16-bit PCM WAV is most compatible

## Reference Files
- `references/generation-performance.md` — Generation timing benchmarks, frame calculations, and speed profiles for RTX 3060 Ti
- `references/heartmula-repo-ids.md` — HuggingFace repo IDs and filenames
- `references/vocal-timbre-limitations.md` — Code archaeology of vocal timbre control
- `references/rl-model-session-2026-05-14.md` — RL模型下载、目录结构准备、推理失败记录

## Related Skills
- `creative/songwriting-and-ai-music` — Lyric writing and Suno AI prompts
- `mlops/models/audiocraft-audio-generation` — Meta MusicGen setup (same task class, different model)
