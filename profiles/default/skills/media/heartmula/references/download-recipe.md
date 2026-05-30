# HeartMuLa Model Download Recipe

## Complete Reusable Script

Save as `download_models.py` in the heartlib project root:

```python
#!/usr/bin/env python3
"""Download HeartMuLa model checkpoints with resume support."""
import os, sys, time, requests
from huggingface_hub import hf_hub_download

BASE = os.path.expanduser("~/.hermes/profiles/lover/home/heartlib/ckpt")
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")

def verify_safetensors(path):
    """Check if a safetensors file is valid (not partial/corrupt)."""
    try:
        from safetensors import safe_open
        with safe_open(path, framework='pt', device='cpu') as f:
            keys = f.keys()
        print(f"    ✓ {os.path.basename(path)}: {len(keys)} tensors valid")
        return True
    except Exception as e:
        print(f"    ✗ {os.path.basename(path)}: CORRUPT — {e}")
        return False

def download_file(repo_id, filename, local_dir, retries=5):
    local_dir = os.path.abspath(os.path.expanduser(local_dir))
    os.makedirs(local_dir, exist_ok=True)
    dest = os.path.join(local_dir, filename)

    # Check if existing file is valid
    if os.path.exists(dest):
        size = os.path.getsize(dest)
        print(f"  ? {filename} exists ({size/1024/1024:.1f}MB), verifying...", flush=True)
        if verify_safetensors(dest):
            print(f"  ✓ {filename} already valid, skipping", flush=True)
            return True
        else:
            print(f"  → Removing corrupt file and re-downloading...", flush=True)
            os.remove(dest)

    # Try huggingface_hub first
    for attempt in range(1, retries + 1):
        try:
            print(f"  ↓ {filename} (hf_hub, attempt {attempt}/{retries})...", flush=True)
            path = hf_hub_download(
                repo_id=repo_id, filename=filename,
                local_dir=local_dir,
            )
            if verify_safetensors(path):
                return True
            else:
                os.remove(path)
                raise ValueError("Corrupt download")
        except Exception as e:
            print(f"  ✗ hf_hub failed: {e}", flush=True)
            if attempt < retries:
                time.sleep(5 * attempt)
    
    # Fallback: direct requests.get download
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    print(f"  ↓ {filename} (direct HTTP fallback)...", flush=True)
    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        downloaded = 0
        with open(dest + '.tmp', 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
        os.rename(dest + '.tmp', dest)
        print(f"  ✓ {filename}: {downloaded/1024/1024:.1f}MB (HTTP)", flush=True)
        if verify_safetensors(dest):
            return True
        else:
            os.remove(dest)
            return False
    except Exception as e:
        print(f"  ✗ HTTP fallback failed: {e}", flush=True)
        return False

def main():
    # HeartMuLa-oss-3B — 4 shards, ~2GB each
    repo1 = "HeartMuLa/HeartMuLa-oss-3B-happy-new-year"
    dir1 = os.path.join(BASE, "HeartMuLa-oss-3B")
    files1 = [f"model-{i:05d}-of-00004.safetensors" for i in range(1,5)]
    print("=== HeartMuLa-oss-3B ===", flush=True)
    for f in files1:
        if not download_file(repo1, f, dir1):
            print("❌ HeartMuLa-oss-3B incomplete", flush=True)
            return False

    # HeartCodec-oss — 2 shards: 4.7GB + 1.6GB ⚠️
    repo2 = "HeartMuLa/HeartCodec-oss-20260123"
    dir2 = os.path.join(BASE, "HeartCodec-oss")
    files2 = [f"model-{i:05d}-of-00002.safetensors" for i in range(1,3)]
    print("\n=== HeartCodec-oss ===", flush=True)
    for f in files2:
        if not download_file(repo2, f, dir2):
            print("❌ HeartCodec-oss incomplete", flush=True)
            return False

    print("\n✅ ALL MODELS DOWNLOADED!", flush=True)
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
```

## How to Run

```bash
# Use ABSOLUTE paths for background processes
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
/home/admin1/.hermes/profiles/lover/home/heartlib/.venv/bin/python \
  /home/admin1/.hermes/profiles/lover/home/heartlib/download_models.py
```

## How to Monitor

While the script is running, check progress:

```bash
# Total size of each model directory (includes .cache)
du -sh /home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B/
du -sh /home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartCodec-oss/

# Check incomplete files (download in progress)
find /home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/ \
  -path "*/download/*.incomplete" -exec du -sh {} \; | sort -rh

# Check completed weight files
ls -lh /home/admin1/.hermes/profiles/lover/home/heartlib/ckpt/HeartMuLa-oss-3B/*.safetensors
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Exit code 127 (command not found) | Background process cwd differs from foreground | Use absolute paths for python and script |
| Exit code 143 (SIGTERM) | `hf download` CLI killed during context compaction | Use Python API instead of CLI |
| `TypeError: resume` | huggingface_hub >= 1.x deprecated `resume` param | Remove `resume=True` |
| `local_dir_use_symlinks` warning | Parameter deprecated | Remove it |
| Stale lock files | Previous interrupted download | `rm -f ckpt/*/.cache/huggingface/download/*.lock` |
| Locks held by ghost process | Background process survived context compaction | `ps aux | grep -i hf` then `kill` |
| Download stalls at 0 bytes | All 4 shards sharing 1 connection | They'll progress — it's sequential within the thread |
| Exit code 124 (timeout) | 600s Hermes terminal timeout for 4.7GB shard | Use `background=true` with longer timeout (7200s) or split into chunks |
| `SafetensorError: incomplete metadata, file not fully covered` | Partial/corrupt download | Delete the file and re-download — `safe_open()` detects this |
| `hf_hub_download` says "already exists" but file is corrupt | No validation in huggingface_hub | Always verify with `safe_open()` — see script above |

## Pitfalls (from real sessions)

1. **Always use absolute paths** in background terminal commands. `cd ~/heartlib` may not resolve as expected.
2. **`resume=True` is deprecated** in huggingface_hub ≥1.x. Just don't pass it — resumption is automatic.
3. **Files appear in `.cache/huggingface/download/*.incomplete` first**, then get moved atomically on completion. Don't panic if you don't see safetensors in the target dir immediately.
4. **Each shard is ~2GB for HeartMuLa**. Total download is ~10-12GB. At ~50-100 Mbps, expect ~15-30 minutes.
5. **No HF_TOKEN set** → lower rate limits but downloads still work.
6. **HeartCodec shard 1 is 4.7GB** (not ~1-2GB). At ~20-30 Mbps, expect 20-30 minutes just for this shard. The 600s Hermes default timeout is insufficient — use `background=true` with `timeout=7200`.
7. **Direct HTTP fallback works when huggingface_hub doesn't**: If `hf_hub_download` fails with "Distant resource does not seem to be on huggingface.co", use `requests.get(url, stream=True)` instead — it bypasses huggingface_hub's proxy/SSL configuration entirely.
8. **Always `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY` before downloads** — WSL may inherit Windows proxy settings that interfere with huggingface.co connections.
9. **safetensors verification is mandatory**: `os.path.getsize()` alone does NOT detect corruption. Always call `safe_open(path, framework='pt', device='cpu')` to validate after any download that may have been interrupted.

