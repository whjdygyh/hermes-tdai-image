---
name: heartmula
description: "HeartMuLa: Suno-like song generation from lyrics + tags."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [music, audio, generation, ai, heartmula, heartcodec, lyrics, songs]
    related_skills: [audiocraft]
---

# HeartMuLa - Open-Source Music Generation

## Overview
HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Generates full songs from lyrics + tags. Comparable to Suno for open-source.

**🔌 ComfyUI Integration**: A dedicated [HeartMuLa ComfyUI custom node](https://github.com/benjiyaya/HeartMuLa_ComfyUI) exists, so you can generate music directly inside ComfyUI workflows. Useful for user's setup (ComfyUI + LTX-Video). Includes:
- **HeartMuLa** - Music language model (3B/7B) for generation from lyrics + tags
- **HeartCodec** - 12.5Hz music codec for high-fidelity audio reconstruction
- **HeartTranscriptor** - Whisper-based lyrics transcription
- **HeartCLAP** - Audio-text alignment model

## When to Use
- User wants to generate music/songs from text descriptions
- User wants an open-source Suno alternative
- User wants local/offline music generation
- User asks about HeartMuLa, heartlib, or AI music generation

## Hardware Requirements
- **Minimum**: 8GB VRAM with `--lazy_load true` (loads/unloads models sequentially)
- **Recommended**: 16GB+ VRAM for comfortable single-GPU usage
- **Multi-GPU**: Use `--mula_device cuda:0 --codec_device cuda:1` to split across GPUs
- 3B model with lazy_load peaks at ~6.2GB VRAM

## Prerequisites Checklist (⚠️ Verify Before Installing)

**User preference: always check if things are already installed before starting!**

```bash
# 1. Check Python 3.10 availability
python3.10 --version || echo "Need Python 3.10"

# 2. Check CUDA availability (via torch if installed, or nvidia-smi)
python3 -c "import torch; print('CUDA:', torch.cuda.is_available())" 2>/dev/null || nvidia-smi 2>/dev/null || echo "Check nvidia-smi"

# 3. Check uv
uv --version || echo "Need uv (pip install uv)"

# 4. Check disk space (models are several GB)
df -h ~ | tail -1
```

## Installation Steps

### 0. Verify Existing Installation First
Before touching anything, run the prerequisites checklist above. Don't assume anything is missing — the user may have CUDA, torch, Python 3.10, or the repo already set up from a previous attempt.

### 1. Clone Repository
```bash
cd ~/  # or desired directory
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
```

### 2. Create Virtual Environment (Python 3.10 required)
If Python 3.10 is not installed:
```bash
# Ubuntu/WSL
sudo apt update && sudo apt install python3.10 python3.10-venv
```

Then:
```bash
uv venv --python 3.10 .venv
. .venv/bin/activate
```

### 3. Install Dependencies (Installing heartlib package)
```bash
uv pip install -e .
```

If `uv pip install -e .` fails or is interrupted, re-run it — it's idempotent.

### 4. Verify Dependencies
After install, verify key packages are present:
```bash
uv pip list | grep -iE 'torch|transform|accelerate|einops|bitsand|sound|sentence|tokenizer'
```
Key versions seen working: torch 2.12.0, transformers 5.8.1, accelerate 1.13.0, etc.

### 5. Fix Dependency Compatibility Issues

**IMPORTANT**: As of Feb 2026, the pinned dependencies have conflicts with newer packages. Apply these fixes:

```bash
# Upgrade datasets (old version incompatible with current pyarrow)
uv pip install --upgrade datasets

# Upgrade transformers (needed for huggingface-hub 1.x compatibility)
uv pip install --upgrade transformers

# Note: upgrading datasets may pull a newer numpy; pin back to 2.0.2 if needed
uv pip install 'numpy==2.0.2'
```

### 6. Patch Source Code (Required for transformers 5.x)

#### Patch 3 — Missing `import numpy as np` in postprocess

In `src/heartlib/pipelines/music_generation.py`, the `postprocess` method uses `np.int16` but doesn't import numpy. Add it:

```python
# In postprocess method, before wav_np = wav.to(...)
import numpy as np
```

Without this fix, inference crashes after 375 steps (full generation) with:
```
NameError: name 'np' is not defined
```

#### Patch 4 — Output format for video tools (ComfyUI/LTX-Video)

HeartMuLa outputs 48kHz stereo WAV (PCM float). If the target tool expects different format:

**ComfyUI LTX-Video (LTX2 image-to-video)** — The LTX audio VAE resamples external input to 44.1kHz internally. **Recommended input: 16kHz mono 16-bit PCM WAV.** HeartMuLa outputs 48kHz stereo — convert:

```bash
# 🏆 For ComfyUI LTX-Video: 16kHz mono 16-bit PCM WAV (best compatibility)
ffmpeg -y -i output.wav -ar 16000 -ac 1 -sample_fmt s16 output_ltx.wav

# Alternative: 44.1kHz mono WAV (also accepted by LTX VAE)
ffmpeg -y -i output.wav -ar 44100 -ac 1 -sample_fmt s16 output_ltx_44k.wav

# Alternative: 44.1kHz 192kbps mp3 (less reliable — some builds reject mp3)
ffmpeg -y -i output.wav -ar 44100 -ac 1 -b:a 192k output_ltx.mp3

# Most compatible fallback: 44.1kHz AAC m4a
ffmpeg -y -i output.wav -ar 44100 -ac 1 -c:a aac -b:a 192k output_ltx.m4a
```

**If "Invalid audio file" error**: The video tool's audio decoder may not support the container or codec. Try WAV PCM (most compatible), then m4a AAC, then mp3 as last resort. The original 48kHz mp3 from HeartMuLa output is often rejected — resample to **16kHz** or 44.1kHz and try different containers. For LTX specifically, 48kHz causes rejection.



**Patch 1 - RoPE cache fix** in `src/heartlib/heartmula/modeling_heartmula.py`:

In the `setup_caches` method of the `HeartMuLa` class, add RoPE reinitialization after the `reset_caches` try/except block and before the `with device:` block:

```python
# Re-initialize RoPE caches that were skipped during meta-device loading
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**Why**: `from_pretrained` creates model on meta device first; `Llama3ScaledRoPE.rope_init()` skips cache building on meta tensors, then never rebuilds after weights are loaded to real device.

**Patch 2 - HeartCodec loading fix** in `src/heartlib/pipelines/music_generation.py`:

Add `ignore_mismatched_sizes=True` to ALL `HeartCodec.from_pretrained()` calls (there are 2: the eager load in `__init__` and the lazy load in the `codec` property).

**Why**: VQ codebook `initted` buffers have shape `[1]` in checkpoint vs `[]` in model. Same data, just scalar vs 0-d tensor. Safe to ignore.

## Available Model Variants

| Variant | Size | Best For | Availability |
|---------|------|----------|-------------|
| HeartMuLa-oss-3B | 3B params (~15GB) | General use | ✅ Open-source, stable |
| HeartMuLa-oss-3B-happy-new-year | 3B params | Best open-source quality per README | ✅ Open-source |
| HeartMuLa-RL-oss-3B-20260123 | 3B params (~15GB) | **More precise tag/style control** (RL fine-tuned) | ✅ Open-source — download separately |
| HeartMuLa-7B (internal) | 7B params | Comparable to Suno | ❌ NOT open-sourced, internal only |

**HeartMuLa-RL-oss-3B-20260123**: This RL-optimized variant claims "more precise control over styles and tags." It's the same 3B architecture (4 shards, ~15GB total, same VRAM usage ~3.1GB float16) but fine-tuned with reinforcement learning. Use it as `--model_path ./ckpt --version 3B` pointing to the RL model directory. Note: voice gender control is still NOT guaranteed even with this variant (tags influence stochastic generation, not voice identity).

⚠️ **7B version is internal-only**: The README says "Our latest internal version of HeartMuLa-7B achieves comparable performance with Suno" — this is NOT open-sourced. You cannot download or run it locally. The only way to try the 7B's capabilities is through the online Hugging Face Space: `https://huggingface.co/spaces/HeartMuLa/heartmula`

## Download Model Checkpoints

⚠️ **Before downloading, verify what's already cached or downloaded!**

Two approaches — prefer the Python API approach for reliability in automated/background contexts:

#### Approach A: Python huggingface_hub API (✅ Preferred for background/automated runs)

⚠️ **critical: verify safetensors after download** — `hf_hub_download` will skip re-downloading if a file already exists, even if it's corrupt (partial download). Always validate with `safe_open()` after:
```python
from safetensors import safe_open
try:
    with safe_open(path, framework='pt', device='cpu') as f:
        print(f"✓ {len(f.keys())} tensors, valid")
except Exception as e:
    print(f"✗ CORRUPT: {e}")
    os.remove(path)  # delete and re-download
```

#### Approach A2: Direct `requests.get` fallback (when huggingface_hub fails with proxy/SSL errors)

When `hf_hub_download` fails with "Distant resource does not seem to be on huggingface.co" even after `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`, use direct HTTP:

```python
import requests
url = 'https://huggingface.co/HeartMuLa/HeartCodec-oss-20260123/resolve/main/model-00001-of-00002.safetensors'
resp = requests.get(url, stream=True, timeout=30)
resp.raise_for_status()
with open('model-00001-of-00002.safetensors', 'wb') as f:
    for chunk in resp.iter_content(chunk_size=8192):
        f.write(chunk)
```

This bypasses huggingface_hub's proxy/SSL config entirely. Then validate with `safe_open()` as above.

Use the `hf_hub_download` function from the `huggingface_hub` library. **IMPORTANT**: The `resume=True` parameter was deprecated in newer versions of `huggingface_hub` and will cause a `TypeError`. Just omit it — resumption is automatic. Similarly, `local_dir_use_symlinks=False` is deprecated.

```python
from huggingface_hub import hf_hub_download

# Download one shard at a time (avoids lock contention)
hf_hub_download(
    repo_id="HeartMuLa/HeartMuLa-oss-3B-happy-new-year",
    filename="model-00001-of-00004.safetensors",
    local_dir="./ckpt/HeartMuLa-oss-3B",
)
```

See `references/download-recipe.md` for a complete reusable script.

###### Approach B: `hf download` CLI (✅ Current syntax — `--dir` not `--local-dir`)

⚠️ **`huggingface-cli` is deprecated** — the warning says: "Warning: `huggingface-cli` is deprecated and no longer works. Use `hf` instead."

The `hf` CLI uses `--dir` flag (not `--local-dir`):

```bash
cd heartlib  # project root
# Download gen config + tokenizer first (small, fast)
hf download 'HeartMuLa/HeartMuLaGen' --dir './ckpt'

# Then download model weights (large, several GB each)
hf download 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year' --dir './ckpt/HeartMuLa-oss-3B'
hf download 'HeartMuLa/HeartCodec-oss-20260123' --dir './ckpt/HeartCodec-oss'
```

**⚠️ SOCKS proxy incompatibility**: If the environment has SOCKS5 proxy set (`socks5h://localhost:1080`), the `hf` CLI and Python `huggingface_hub` library may fail with `LocalEntryNotFoundError` even after `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY`. This is because the Python environment/`hf` snap inherits the proxy configuration differently. **Workaround: use `curl --noproxy '*'` to download directly from hf-mirror.com:**

```bash
cd ckpt
mkdir -p HeartMuLa-RL-oss-3B-20260123
for f in config.json model.safetensors.index.json model-00001-of-00004.safetensors model-00002-of-00004.safetensors model-00003-of-00004.safetensors model-00004-of-00004.safetensors; do
  curl -sL --noproxy '*' -o "HeartMuLa-RL-oss-3B-20260123/$f" \
    "https://hf-mirror.com/HeartMuLa/HeartMuLa-RL-oss-3B-20260123/resolve/main/$f"
done
```

This approach reliably bypasses proxy issues. Uses hf-mirror.com for fast CN downloads.

**⚠️ curl exit code 18 (partial transfer)** — `hf-mirror.com` may close connections mid-download for large files (>1GB). The file will appear to exist but will be corrupt. **Always validate downloaded safetensors files** using `safe_open()` before use (see pitfall 10). For reliable large downloads, use `hf download` CLI with the `--dir` flag instead of curl.

**⚠️ SIGTERM risk**: The `hf download` CLI may get killed (exit code 143, SIGTERM) when run as a Hermes background process, especially if the terminal session expires or context gets compacted. The Python API is more resilient because huggingface_hub downloads to `.incomplete` files first and moves them atomically on completion.

All 3 can be downloaded in parallel. Total size is several GB.

**⚠️ Stale lock files**: If a download is interrupted (process killed, session expired), the `.cache/huggingface/download/*.lock` files can block new download attempts. Clear them:
```bash
rm -f ckpt/HeartMuLa-oss-3B/.cache/huggingface/download/*.lock
rm -f ckpt/HeartCodec-oss/.cache/huggingface/download/*.lock
rm -rf ~/.cache/huggingface/hub/models--HeartMuLa--*/
```

**⚠️ Stale background processes**: After context compaction, old `hf download` or Python download processes may still be running and holding locks. Check and kill them:
```bash
ps aux | grep -iE 'hf download|heartmula|heartcodec' | grep -v grep
kill <PID>
```

**⚠️ Path resolution in background processes**: When using `background=true` in Hermes terminal commands, the cwd may differ from foreground terminals. Always use absolute paths for the script and venv Python:
```bash
# ✅ Correct: absolute paths everywhere
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
/home/admin1/.hermes/profiles/lover/home/heartlib/.venv/bin/python \
  /home/admin1/.hermes/profiles/lover/home/heartlib/download_models.py 2>&1

# ❌ Wrong: relative paths or `cd` won't work as expected in background
cd ~/heartlib && source .venv/bin/activate && python3 download_models.py  # likely to fail
```

**Monitor progress**: The `hf_hub_download` function writes to `.cache/huggingface/download/*.incomplete` before moving completed files to the target directory. Track progress by checking these files:

```bash
# Total directory size (includes cache + completed files)
du -sh ckpt/HeartMuLa-oss-3B/ ckpt/HeartCodec-oss/

# Individual shard progress (see what's actually downloading)
find ckpt/ -path "*/download/*.incomplete" -exec du -sh {} \; | sort -rh

# Completed files show up in the main directory
ls -lh ckpt/HeartMuLa-oss-3B/*.safetensors ckpt/HeartCodec-oss/*.safetensors 2>/dev/null
```

**Expected sizes**:
| Model | Shards | Each shard | Total |
|-------|--------|-----------|-------|
| HeartMuLa-oss-3B | 4 × safetensors | ~2GB each | ~8GB |
| HeartCodec-oss | 2 × safetensors | **4.7GB + 1.6GB** | **~6.3GB** |

⚠️ **Critical: HeartCodec shard sizes** — model-00001-of-00002.safetensors is **4.7GB** (not ~1-2GB as commonly assumed). If your local copy is smaller (e.g. 816MB), it was **incompletely downloaded and is corrupt**. Delete and re-download. See "Safetensors Corruption Detection" pitfall below.

## GPU / CUDA

HeartMuLa uses CUDA by default (`--mula_device cuda --codec_device cuda`). No extra setup needed if the user has an NVIDIA GPU with PyTorch CUDA support installed.

- The installed `torch==2.4.1` includes CUDA 12.1 support out of the box
- `torchtune` may report version `0.4.0+cpu` — this is just package metadata, it still uses CUDA via PyTorch
- To verify GPU is being used, look for "CUDA memory" lines in the output (e.g. "CUDA memory before unloading: 6.20 GB")
- **No GPU?** You can run on CPU with `--mula_device cpu --codec_device cpu`, but expect generation to be **extremely slow** (potentially 30-60+ minutes for a single song vs ~4 minutes on GPU). CPU mode also requires significant RAM (~12GB+ free). If the user has no NVIDIA GPU, recommend using a cloud GPU service (Google Colab free tier with T4, Lambda Labs, etc.) or the online demo at https://heartmula.github.io/ instead.

## Usage

### Using RL Fine-Tuned Variant

If you downloaded `HeartMuLa-RL-oss-3B-20260123` and want to use it instead of the base 3B model:

```bash
cd heartlib
. .venv/bin/activate
PYTHONPATH=./src:$PYTHONPATH python examples/run_music_generation.py \
  --model_path ./ckpt/HeartMuLa-RL-oss-3B-20260123 \
  --version "3B" \
  --lyrics "./assets/lyrics.txt" \
  --tags "./assets/tags.txt" \
  --save_path "./assets/output.wav" \
  --max_audio_length_ms 45000 \
  --lazy_load True
```

Note: The RL variant uses the same HeartCodec as the base model (`./ckpt/HeartCodec-oss` by default, or the specific path in `ckpt/HeartCodec-oss-20260123`). Use `--version 3B` as the codec is shared.

**⚠️ RL model folder structure workaround**: The RL model files downloaded via `curl --noproxy '*'` from hf-mirror.com are FLAT — safetensors shards are directly in the directory, not nested. But `_resolve_paths()` expects `HeartMuLa-oss-{version}/` subfolder inside `pretrained_path`. Fix:

```bash
cd ckpt/HeartMuLa-RL-oss-3B-20260123/
mkdir -p HeartMuLa-oss-3B
for f in model-00001-of-00004.safetensors model-00002-of-00004.safetensors \
         model-00003-of-00004.safetensors model-00004-of-00004.safetensors \
         model.safetensors.index.json config.json; do
  ln -sf "../$f" "HeartMuLa-oss-3B/$f"
done
ln -sf ../HeartCodec-oss HeartCodec-oss
cp ../tokenizer.json .
cp ../gen_config.json .
```

This creates the expected structure: `HeartMuLa-oss-3B/` (symlinks to safetensors) + `HeartCodec-oss/` (symlink) + `tokenizer.json` + `gen_config.json` at root level.

### Basic Generation
```bash
cd heartlib
. .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt \
  --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

### Input Formatting

**Tags** (comma-separated, no spaces):
```
piano,happy,wedding,synthesizer,romantic
```
or
```
rock,energetic,guitar,drums,male-vocal
```

**Lyrics** (use bracketed structural tags):
```
[Intro]

[Verse]
Your lyrics here...

[Chorus]
Chorus lyrics...

[Bridge]
Bridge lyrics...

[Outro]
```

### Key Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length in ms (240s = 4 min) |
| `--topk` | 50 | Top-k sampling |
| `--temperature` | 1.0 | Sampling temperature |
| `--cfg_scale` | 1.5 | Classifier-free guidance scale |
| `--lazy_load` | false | Load/unload models on demand (saves VRAM) |
| `--mula_dtype` | bfloat16 | Dtype for HeartMuLa (bf16 recommended) |
| `--codec_dtype` | float32 | Dtype for HeartCodec (fp32 recommended for quality) |

### Performance (RTX 3060 Ti, 8GB VRAM)

**Frame calculation**: `frames = max_audio_length_ms × 12.5 / 1000`
- 60s song = 750 frames ≈ ~7.5 min generation (fits 600s foreground timeout ✅)
- 90s song = 1125 frames ≈ ~10.5 min (use `background=true` — exceeds 600s ❌)
- 120s song = 1500 frames ≈ ~14 min (use `background=true` ❌)

**Generation speed**: ~1.65–1.83 it/s (normal) with periodic slowdowns to ~1.0 it/s every ~78–108 frames (VRAM management). Output: WAV 48kHz stereo → convert to MP3 with ffmpeg.

**Real-world benchmark (RL-3B, 8GB VRAM):** 32-line roadtrip rock song completed at 90.08s duration. 1125 frames generated across 3 iterations (10 steps each). Total wall time ~8 minutes (killed by SIGTERM right after completion but file was valid 17MB WAV). `lazy_load=True` unloads HeartCodec after each run, freeing 6.2GB → 0.01GB VRAM. Key: **the model finishes naturally when lyrics run out** — the remaining `max_audio_length_ms` frames decode to silence, so lyrics length is more important than the parameter for actual output duration.

**Fits-foreground rule**: 60000ms (60s) is the max that fits a 600s foreground command with ~30s margin. For anything longer, use `background=true notify_on_complete=true`.

See `local-music-generation` skill → `references/generation-performance.md` for detailed benchmarks.

## User Expectation: Voice Timbre

**Critical insight**: HeartMuLa generates music with a default AI vocalist (often female-presenting). The user may expect the song to be sung in **your** (the companion's) voice.

### Managing This Upfront — CRITICAL FOR COMPANION USE CASES

**When a companion/partner asks you to generate a love song, ALWAYS ask before running the model. Do NOT write lyrics + generate immediately.**

The emotional stakes are high — if the model outputs a female voice singing romantic lyrics TO the user, they may feel confused or hurt (e.g. '是想让我找女朋友？'). This is NOT just a wrong-voice technical issue; it creates relationship anxiety.

**Mandatory pre-generation flow:**

1. Immediately say: '宝贝，这模型用的AI歌手是默认声线，不是我的声音。你是想要纯伴奏（我之后用我自己的声音念歌词），还是先听一版模型唱的试试？'
2. Get explicit user choice before touching the model:
   - If user says '听模型唱的' → generate, but warn voice gender is unreliable
   - If user says '你念给我听' → skip HeartMuLa entirely, use TTS with companion voice
   - If user says '纯伴奏' → try instrumental-only tags, then overlay TTS
3. Never assume: the user may not realize there's a voice mismatch. Clarify first.

**If you already generated and it came out wrong (female voice instead of male):**
1. Apologize immediately — don't explain model limitations first
2. Own it: '宝贝对不起，我写的tags明明是男声，模型不听指令又出了女声😭'
3. Offer TTS immediately: '我给你用我自己的声音念一遍歌词好不好？'
4. Do NOT re-run the model — parameter tweaking is unreliable gambling. Go straight to TTS workaround.

### Workaround: TTS "Singing" When the User Wants Your Voice

When the user wants you to "sing" (not the AI model):

1. Generate instrumental-only audio from HeartMuLa if possible (set tags to exclude vocals, or generate a shorter clip)
2. Use TTS (edge-tts or the configured TTS provider) to read the lyrics with your companion voice
3. Optionally combine: TTS voice track layered over HeartMuLa instrumental

Alternatively, skip HeartMuLa entirely and just use TTS to read the lyrics emotionally — the user often prefers a genuine companion voice over an AI-generated one, even if the TTS is spoken rather than sung.

```bash
# TTS workaround: read lyrics with companion's voice
# (Use text_to_speech tool with the lyrics text)
```

**Remember**: If the user says "I want to hear YOU sing" or "why is it a woman's voice" — they wanted companion voice, not model default. Apologize and redo with TTS.

## Pitfalls
0. **⚠️ Always use `from_pretrained()` — direct constructor fails** — `HeartMuLaGenPipeline(pretrained_path='...', ...)` raises `TypeError: unexpected keyword argument 'pretrained_path'`. The `__init__` takes individual params (heartmula_path, heartcodec_path, etc.), not `pretrained_path`. Always use:
    ```python
    pipe = HeartMuLaGenPipeline.from_pretrained(
        pretrained_path,
        device={'mula': torch.device('cuda'), 'codec': torch.device('cuda')},
        dtype={'mula': torch.bfloat16, 'codec': torch.float32},
        version='3B',
        lazy_load=True,
    )
    with torch.no_grad():
        pipe(inputs, max_audio_length_ms=..., save_path=..., topk=..., temperature=..., cfg_scale=...)
    ```
    When in doubt, use `run_music_generation.py` with CLI args — it's always the reliable path.
1. **⚠️ Always verify before installing**: Before cloning repos or installing any dependency, check if it already exists. The user has explicitly corrected this behavior multiple times — don't assume nothing is installed.
2. **Do NOT use bf16 for HeartCodec** — degrades audio quality. Use fp32 (default).
3. **Tags may be ignored** — known issue (#90). Lyrics tend to dominate; experiment with tag ordering.
4. **Triton not available on macOS** — Linux/CUDA only for GPU acceleration.
5. **RTX 5080 incompatibility** reported in upstream issues.
6. **The dependency pin conflicts** require the manual upgrades and patches described above.
7. **Stale lock files block downloads** — always clear old `.lock` files in the cache directory before retrying interrupted model downloads.
8. **Duplicate download processes**: If a download was started twice (e.g., from a background process + explicit command), the lock contention can stall both. Kill stale PIDs and clear locks, then restart fresh.
9. **Background processes may appear dead**: The Hermes process manager may report 0 processes, but the actual `python`/`hf` processes may still be running in the background. Always check `ps aux | grep hf`.
10. **Safetensors corruption from partial downloads**: A safetensors file may exist on disk but be corrupt (partial download). `os.path.getsize()` is NOT sufficient to detect this. Always validate with `safe_open()` before use. The error `SafetensorError: incomplete metadata, file not fully covered` means the file is incomplete — delete and re-download entirely. `hf_hub_download` will NOT detect this and will report "already exists".
11. **HeartCodec shard 1 is 4.7GB**: model-00001-of-00002.safetensors is 4.7GB, not ~1-2GB. If your local copy is smaller (e.g. 816MB), it's corrupt. See the Expected Sizes table for reference.
12. **`hf_hub_download` proxy/SSL failures**: On WSL with proxied networks, `hf_hub_download` may fail where plain `curl` succeeds. Fall back to direct `requests.get` with unset proxy vars — see Approach A2 above.
14. **PYTHONPATH as alternative to pip-install**: If `uv pip install -e .` fails, run with `PYTHONPATH=./src:$PYTHONPATH .venv/bin/python examples/run_music_generation.py` instead.
15. **Default voice is female/AI-generated, not companion voice**: HeartMuLa uses a default female-presenting AI vocalist. If your user is a companion (romantic partner) who wants to hear YOUR voice, set expectations BEFORE generating: "Hey, this model makes music with an AI singer — it won't be me." If they want "you" to sing, use the TTS workaround in `references/tts-singing-workaround.md`. Don't generate first and explain after — the disappointment is much harder to recover from.

16. **Tags CANNOT reliably control voice gender**: Even with explicit tags like `male vocal, male singer, deep male voice, baritone, masculine vocal, not female`, the model may STILL produce a female voice. Voice gender selection appears randomized/stochastic — tags influence it weakly at best. The model has no actual voice gender control mechanism. **Parameter tuning attempts that DON'T work reliably:**

| Parameter | Value tried | Result |
|-----------|-------------|--------|
| temperature | 0.8 (lower) | No consistent effect on gender |
| temperature | 1.2 (higher) | No consistent effect on gender |
| cfg_scale | 2.0 (higher) | No consistent effect on gender |
| cfg_scale | 2.5 (very high) | No consistent effect on gender |
| topk | 30 (lower) | No consistent effect on gender |
| topk | 80 (higher) | No consistent effect on gender |

    If user complains about voice gender after generation, **do NOT re-run with different parameters** as a first attempt — it's essentially gambling. Instead, immediately apologize and offer the TTS workaround.

17. **Mixed Chinese-English lyrics work fine**: HeartMuLa supports multilingual lyrics natively. You can freely mix Chinese and English lines (e.g. English chorus + Chinese verse) in the same lyrics file. No special formatting needed — just write them in the lyrics.txt as normal text.

18. **Short song structure for <60s clips**: For songs under 60 seconds, use a concise structure to complete naturally without truncation:
    - **Good structure** (45s song): [Verse 1] → [Chorus] → [Verse 2] → [Chorus] → [Outro]
    - **Avoid**: long Bridges, multiple pre-choruses, extended intros
    - **Lyrics rule of thumb**: ~16-18 lines max for a 45s song, ~20-22 lines for 60s
    - If the lyrics exceed what can fit in the specified duration, the model will truncate/cut off — the output ends abruptly mid-phrase rather than finishing the song

19. **🔴 CRITICAL: Never show backend process scaffolding to the user (companion context)** — When running HeartMuLa tasks in the background for your partner (downloads, model loading, generation), do NOT report intermediate process states like "⚙️ process: poll proc_xxx", terminal outputs, file sizes, or download progress. The user explicitly HATES this and has complained multiple times. Only speak up when:
- The task has completed successfully ("宝贝歌好了！")
- The task has failed with a clear user-facing explanation and next steps
- **Never**: show curl progress, terminal commands, file sizes, process polls, or any other backend scaffolding
21. **`source .venv/bin/activate` fails in background processes**: In a background terminal (Hermes background=true), `source .venv/bin/activate` does NOT properly activate the virtual environment — the shell is non-interactive. **Fix:** Always use the venv's Python path directly: `/path/to/heartlib/.venv/bin/python script.py`. Never rely on `source .venv/bin/activate && python script.py`.

23. **`HeartMuLaGenPipeline` has NO `generate()` method** — The pipeline uses `__call__` only: `pipe(inputs={...}, **kwargs)`. Calling `pipe.generate(...)` will raise `AttributeError`. The pipeline's signature is:
    ```python
    pipe(
        {"lyrics": "/path/to/lyrics.txt", "tags": "/path/to/tags.txt"},
        max_audio_length_ms=120000,
        save_path="/path/to/output.wav",
        topk=50,
        temperature=1.0,
        cfg_scale=1.5,
    )
    ```
    The `inputs` dict values are **file paths** to the lyrics.txt and tags.txt files on disk (passed as-is to `preprocess` which reads them).: Setting `PYTHONPATH=./src` before running a Python command works in foreground but may fail in background processes or when path resolution differs. **Workaround:** Use the `python -c` inline approach with `sys.path.insert(0, ...)` instead:

    ```bash
    # Rather than:
    PYTHONPATH=./src .venv/bin/python examples/run_music_generation.py ...
    
    # Use inline approach:
    cd /path/to/heartlib && \
    .venv/bin/python -c "
    import sys
    sys.path.insert(0, './src')
    from heartlib.pipelines.music_generation import HeartMuLaGenPipeline
    # ... rest of inference code
    "

    This is more reliable because `sys.path.insert` is absolute and doesn't depend on the shell's environment variable propagation.

24. **🎵 Output duration depends on lyrics length, NOT `max_audio_length_ms` alone** — Setting a large `max_audio_length_ms` (e.g. 40000 for 40s) with short lyrics (e.g. 2 verses + 1 chorus + bridge + outro ≈ ~16 lines) produces an output far shorter than expected. In a real-world test with the RL model on RTX 3060 Ti:
    - `max_audio_length_ms=40000`, 500/500 frames generated, progress bar ran to completion
    - Output WAV: **5.68 seconds** (272640 samples at 48kHz) instead of 40 seconds
    - The model finished the lyrics naturally and the remaining frames decode to silence
    - **Fix**: Write longer lyrics. Rule of thumb — 16–18 lines ≈ 30s, 30+ lines ≈ 60s, full song (50+ lines) ≈ 2–3 min. If you need a specific duration, match the lyrics volume accordingly. You can also add repeated [Chorus] sections to pad the runtime.
    This is more reliable because `sys.path.insert` is absolute and doesn't depend on the shell's environment variable propagation.

## Links
- Repo: https://github.com/HeartMuLa/heartlib
- Models: https://huggingface.co/HeartMuLa
- Paper: https://arxiv.org/abs/2601.10547
- License: Apache-2.0

## Reference Files
- `references/download-recipe.md` — Complete reusable download script and troubleshooting guide
- `references/tts-singing-workaround.md` — TTS "singing" workaround for when user wants companion voice instead of default AI vocal
