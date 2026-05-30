# HeartMuLa Repo IDs & Download Details

## Key Repositories (Mirror-Compatible)

| Model | HF Repo ID | Files | Total Size |
|-------|-----------|-------|------------|
| HeartMuLa 3B (base) | `HeartMuLa/HeartMuLa-oss-3B-happy-new-year` | 4 x .safetensors | ~15 GB |
| HeartMuLa 3B (RL) | `HeartMuLa/HeartMuLa-RL-oss-3B-20260123` | 4 x .safetensors | ~12 GB |
| HeartCodec | `HeartMuLa/HeartCodec-oss-20260123` | 2 x .safetensors | ~6.3 GB |

**RL model config** (from config.json): llama-3B backbone, llama-300M decoder, same architecture as base. torch_dtype = float32.

## RL Model File Details

| File | Size | Corruption Risk |
|------|------|-----------------|
| model-00001-of-00004.safetensors | ~1.3 GB | ⚠️ HIGH — most commonly corrupt |
| model-00002-of-00004.safetensors | ~4.6 GB | Low |
| model-00003-of-00004.safetensors | ~4.6 GB | Low |
| model-00004-of-00004.safetensors | ~907 MB | Low |
| model.safetensors.index.json | 23 KB | N/A |
| config.json | 308 B | N/A |

## File Sizes (Measured, 2026-05-13)

**HeartMuLa-oss-3B:**
- model-00001-of-00004.safetensors: ~4.7 GB
- model-00002-of-00004.safetensors: ~4.7 GB
- model-00003-of-00004.safetensors: ~4.7 GB
- model-00004-of-00004.safetensors: ~907 MB

**HeartCodec-oss-20260123:**
- model-00001-of-00002.safetensors: ~4.7 GB (⚠️ most commonly corrupt)
- model-00002-of-00002.safetensors: ~1.6 GB

## Critical: Safetensors Corruption Detection

`hf_hub_download()` does NOT validate files. If a file was partially downloaded
(SIGTERM, timeout), it's silently skipped on re-download since the file exists.

**Detection script:**
```python
from safetensors import safe_open

def verify_safetensor(path):
    """Returns True if valid, deletes and returns False if corrupt."""
    try:
        with safe_open(path, framework='pt', device='cpu') as f:
            n = len(f.keys())
            print(f"✓ {path}: {n} tensors valid")
            return True
    except Exception as e:
        print(f"✗ CORRUPT: {path} — {e}")
        os.remove(path)
        return False
```

**Common corruption symptom:** "incomplete metadata, file not fully covered"
→ file was cut off mid-write.

## Common Download Pitfalls

1. **Wrong repo ID** — original code used `HeartMuLa/HeartCodec-oss` (no date suffix).
   The correct ID is `HeartMuLa/HeartCodec-oss-20260123`. The `download_models.py`
   script in the repo has the correct IDs.

2. **huggingface_hub SSL/proxy failures** — even after `unset http_proxy`,
   the library may fail where `requests.get()` works fine. Fallback to curl/wget
   from hf-mirror.com.

3. **hf-mirror.com speed** — ~2-3 MB/s, so a 4.7GB file takes 25-40 minutes.

4. **Gated/private repos** — hf-mirror.com redirects to huggingface.co for
   non-public repos, which requires `HF_TOKEN`. Set via:
   ```bash
   export HF_TOKEN=hf_xxxxxxxx
   ```

5. **Background process path nesting** — Hermes background `terminal` tasks
   run from `~/.hermes/profiles/lover/home/`, not `/home/admin1/` or `~`.
   Always use hardcoded absolute paths for downloads in background scripts.
