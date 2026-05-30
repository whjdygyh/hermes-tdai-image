# SD Model Download from hf-mirror.com (Limited Network)

## Use Case
HuggingFace (huggingface.co) is blocked/timeout; hf-mirror.com works. Need to download SD models and load with Diffusers.

## Key Tools
- `wget -c` (continue/resume) for individual files
- `huggingface_hub` via `HF_ENDPOINT=https://hf-mirror.com`
- Python fallback with `urllib.request` for wget-unfriendly envs

## Method 1: huggingface_hub (preferred, when stable)
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id='SG161222/Realistic_Vision_V6.0_B1_noVAE',
    cache_dir='/path/to/cache',
    local_dir='/path/to/output',
)
```

**Issue**: hf-mirror.com connection can drop mid-download. `snapshot_download` retries but may fail on 4GB+ files.

## Method 2: wget (more reliable for large files)
```python
import os, urllib.request, time

BASE = 'https://hf-mirror.com'
REPO = 'SG161222/Realistic_Vision_V6.0_B1_noVAE'
OUT = '/tmp/model_dir'

files = [
    'model_index.json',
    'vae/diffusion_pytorch_model.bin',
    'text_encoder/pytorch_model.bin',
    'unet/diffusion_pytorch_model.bin',
    'safety_checker/pytorch_model.bin',
]
for f in files:
    url = f'{BASE}/{REPO}/resolve/main/{f}'
    out_path = f'{OUT}/{f}'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    os.system(f'wget -c -q --timeout=30 "{url}" -O "{out_path}"')
```

## Critical: Model Type Detection

### Realistic Vision V6.0 B1 — Delta Weights, NOT Full Checkpoint
- **⚠️ CRITICAL**: This is a DELTA WEIGHTS checkpoint (UNet ONLY, 686 tensors), NOT a full model (1131 tensors would be full).
- Contains ONLY `model.diffusion_model.*` keys — no VAE (`first_stage_model.*`), no TextEncoder (`cond_stage_model.*`)
- Verification: `len(safetensors.torch.load_file('Realistic_Vision_V6.0_NV_B1.safetensors').keys()) == 686`
- On hf-mirror, the file is downloaded as `unet/diffusion_pytorch_model.bin` (NOT .safetensors!)

### ✅ CORRECT Loading Method: Inject into SD1.5 Pipeline
```python
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from safetensors.torch import load_file
import torch

SD15_DIR = "/tmp/ms_cache_sd15/AI-ModelScope/stable-diffusion-v1-5/"
pipe = StableDiffusionPipeline.from_pretrained(
    SD15_DIR, torch_dtype=torch.float16,
    safety_checker=None, requires_safety_checker=False,
)

RV6_FILE = "/tmp/ms_cache_rv6/SG161222/Realistic_Vision_V6.0_B1_noVAE/unet/diffusion_pytorch_model.bin"
sd = load_file(RV6_FILE)
unet_keys = {k: v for k, v in sd.items() if k.startswith('model.diffusion_model')}
pipe.unet.load_state_dict(unet_keys, strict=False)

pipe.scheduler = DPMSolverMultistepScheduler.from_config(
    pipe.scheduler.config, algorithm_type="sde-dpmsolver++"
)
pipe = pipe.to("cuda")
pipe.enable_attention_slicing()
```

### Verifying File Format
```bash
xxd /path/to/diffusion_pytorch_model.bin | head -1
# Shows safetensors header (metadata length) confirming it's valid safetensors format
```

### Full Pipeline Models (DreamShaper 8)
`Lykon/dreamshaper-8` is a complete diffusers pipeline — includes VAE, TextEncoder, UNet, SafetyChecker. Can be loaded with `from_pretrained()` directly.

**⚠️ CRITICAL: .fp16.safetensors File Renaming**
```bash
cd /tmp/ds8_cache
mv unet/diffusion_pytorch_model.fp16.safetensors unet/diffusion_pytorch_model.safetensors
mv vae/diffusion_pytorch_model.fp16.safetensors vae/diffusion_pytorch_model.safetensors
mv text_encoder/model.fp16.safetensors text_encoder/model.safetensors
mv safety_checker/model.fp16.safetensors safety_checker/model.safetensors
```

**Scheduler Incompatibility Fix**:
```python
pipe.scheduler = DEISMultistepScheduler.from_config(
    pipe.scheduler.config, final_sigmas_type="sigma_min"
)
```

### Model Files List (DreamShaper 8 fp16, ~2.5GB total)
```python
files = [
    "model_index.json",
    "feature_extractor/preprocessor_config.json",
    "safety_checker/config.json",
    "safety_checker/model.fp16.safetensors",
    "scheduler/scheduler_config.json",
    "text_encoder/config.json",
    "text_encoder/model.fp16.safetensors",
    "tokenizer/merges.txt",
    "tokenizer/special_tokens_map.json",
    "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json",
    "unet/config.json",
    "unet/diffusion_pytorch_model.fp16.safetensors",
    "vae/config.json",
    "vae/diffusion_pytorch_model.fp16.safetensors",
]
```

## Pitfalls
1. **hf-mirror.com connection drops** for large files (>4GB): curl hits 63-83% then disconnects (`transfer closed with N bytes remaining`). Use wget with `--tries=0` (unlimited retries), `--timeout=120`, `--retry-connrefused`, and `-c` (resume). The `hf` CLI can also hang for 20+ minutes with no output and no progress.
2. **Always validate safetensors after download**: network drops cause partial writes. Use `safe_open(file, framework="pt", device="cpu").keys()` to verify. Corruption error: `SafetensorError: Error while deserializing header: incomplete metadata, file not fully covered`
3. **Realistic Vision V6.0 B1 from hf-mirror is NOT safetensors file** — it's converted to .bin during download.
3. **diffusers 0.37.1 + .bin**: model_index.json references .safetensors but .bin is on disk. Use symlinks.
4. **RTX 3060 Ti 8GB VRAM**: SD1.5 works at 512×768. DO NOT use SDXL (OOM). Enable `enable_attention_slicing()`.
5. **full downloads** with `local_dir_use_symlinks=False` — no shared cache dedup.
