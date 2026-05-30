# HeartMuLa Setup — 2026-05-13 Session Log

## Environment
- WSL Ubuntu 22.04, RTX 3060 Ti 8GB, CUDA 11.5
- Python 3.10 venv, uv 0.11.7
- Network: socks5 proxy on localhost:1080 (must unset for HF/pip)

## Repos & Paths
- Source: `~/.hermes/profiles/lover/home/heartlib/`
- Venv: `~/.hermes/profiles/lover/home/heartlib/.venv/`
- Checkpoints: `~/.hermes/profiles/lover/home/heartlib/ckpt/`

## Download Session Timeline

### Attempt 1: `hf download` CLI
- `hf download HeartMuLa/... --local-dir './ckpt/...'`
- Killed by SIGTERM (exit 143) with `tcsetattr: Inappropriate ioctl for device`
- Partial files left in `.cache/huggingface/download/` as `.incomplete` files

### Attempt 2: Python script with `resume=True`
- Failed: `resume` keyword argument deprecated in newer huggingface_hub

### Attempt 3: Python script without `resume`
- HeartMuLa (15GB): **Completed!** 4 files ÷ 3 × 4.7GB + 1 × 907MB
  - But files written to **nested path** due to background process cwd bug
  - Had to `mv` (not `cp` — times out on 15GB) to correct location
- HeartCodec: **Failed** — killed before completing (process timeout/SIGTERM)

### Attempt 4-5: HuggingFace CLI & Python (SSL/proxy issue)
- `huggingface-cli download` → "deprecated and no longer works. Use `hf` instead."
- `hf download HeartMuLa/HeartCodec-oss-20260123 --local-dir ...` → seemed to hang, no progress
- Python `hf_hub_download` → `LocalEntryNotFoundError` / `FileMetadataError` — SSL/proxy config issue in huggingface_hub library

### Attempt 6: `requests`-based download (SUCCESS)
```python
import requests
r = requests.get(url, stream=True, timeout=30)
# 8MB chunk streaming, resume support via Range header
```
Works when `huggingface_hub` library fails. Uses Hugging Face direct S3 URLs.

## Current State (End of Session)
- ✅ HeartMuLa-oss-3B: 4 safetensors files in correct location (~15GB)
- ⏳ HeartCodec-oss: downloading via `curl` from hf-mirror (4.7GB, background, with lenient timeouts)
- ❌ Audio-to-video test with LTX Video: NOT done (HeartMuLa setup took entire session)

## Session Continuation (2026-05-13, ~22:00)

### HeartCodec model-00001 Re-download (Attempts 7+)
- Previous download via `requests` produced corrupt file (validation failed with "incomplete metadata, file not fully covered")
- Downloaded 4702.1MB but safetensors safe_open detected corruption
- **Try 8:** `hf_hub_download` API via huggingface_hub (with HF_ENDPOINT=hf-mirror.com) — started but no output in 6 min, killed
- **Try 9:** curl with `-o /dev/null` bug (double -o flag) — killed
- **Try 10:** curl with lenient timeouts — reached 83% (3925MB) over ~42min then stalled below 1KB/s, "transfer closed with 1793177455 bytes remaining"
- **Try 11:** huggingface-cli → said "deprecated, use hf instead"
- **Try 12:** `hf download HeartMuLa/HeartCodec-oss-20260123 --local-dir ckpt/HeartCodec-oss model-00001-of-00002.safetensors` — zero output for 24+ minutes (only printed auth warning), killed with SIGTERM
- **Try 13:** `hf download` with `HF_ENDPOINT=https://huggingface.co` (direct, not mirror) — foreground timeout at 5 min with no output
- **Try 14 (running, end of session):** wget with `--tries=0 --timeout=120 --read-timeout=120 --retry-connrefused -c` from hf-mirror

### Key Learnings from Session Continuation
1. **hf-mirror consistently closes connections at various stages** — 99%, 83%, 63% all observed. Error is always "transfer closed with N bytes remaining" (server-side, not client timeout).
2. **`hf` CLI is unreliable from China** — hangs for 24+ minutes with zero output. Even with `HF_ENDPOINT=hf-mirror.com`, produces auth warning then nothing.
3. **Direct HuggingFace also times out** — 5 min with no output from China.
4. **modelscope (魔搭)** does NOT have HeartMuLa/HeartCodec models — not mirrored there.
5. **wget with `--tries=0` is the best bet** — unlimited retries + auto-resume should eventually get the full file through intermittent connections.

### Key Learnings
1. **curl from hf-mirror stalls at high %** — reached 3925MB/4702MB (83%) before speed dropped below 1KB/s and standard `--speed-time 30 --speed-limit 1000` aborted. Use `--speed-time 60 --speed-limit 500`.
2. **safetensors safe_open is the only reliable validation** — `os.path.getsize()` alone misses corruption from interrupted downloads that appear complete.
3. **Double `-o` flags in curl** — second `-o` overrides first. Don't mix `-# -o /dev/null` as progress wrapper with actual `-o file`.

## LTX Video Audio Requirements
- ComfyUI LTX Video: use **16kHz, 16-bit PCM, mono WAV** (verified in comfyui/audio-nodes.md)
- The LTX VAE resamples 16kHz input to internal 44.1kHz automatically
- **48kHz audio is specifically rejected** by LTX pipeline nodes
- Generic LoadAudio supports: mp3, wav, ogg, opus, flac, m4a, aac (PyAV backend)
- Convert: `ffmpeg -i input.ogg -ar 16000 -ac 1 -sample_fmt s16 output_ltx.wav`
