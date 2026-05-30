# Generation Performance Benchmarks (RTX 3060 Ti, 8GB VRAM)

Measured on: WSL2 Ubuntu 22.04, CUDA 11.5, HeartMuLa 3B + HeartCodec, lazy_load=True, float16

## Frame Calculation

```
frames = max_audio_length_ms × 12.5 / 1000
```

| Duration | Frames | Est. Time | Fits 600s Foreground? |
|----------|--------|-----------|----------------------|
| 30s      | 375    | ~3.5 min  | ✅ Yes |
| 60s      | 750    | ~7.5 min  | ✅ Yes (safe margin) |
| 90s      | 1125   | ~10.5 min | ❌ No — use background=true |
| 120s     | 1500   | ~14 min   | ❌ No — use background=true |
| 180s     | 2250   | ~21 min   | ❌ No — use background=true |

## Per-Segment Speed Profile

Generation speed is **NOT uniform**. The process has two phases within each generation:

### Normal Phase (~1.65–1.83 it/s) — ~93% of frames
- Most frames generate at consistent speed
- Brief ramp-up from ~1.61 → 1.83 it/s over first 5 frames
- Rarely peaks at 1.84 it/s

### Slow Phase (~1.0–1.2 it/s) — ~2% of frames (periodic)
- Occurs roughly every 78–108 frames (at frame 99, 158, 218, 278, 338, 398, 457, 517, 576, 636, 696)
- Lasts ~2–5 frames each
- Likely VRAM management / checkpoint sync — GPU reallocates internal buffers
- Speed drops to ~1.0–1.5 it/s, with individual frames as slow as ~1.0 it/s

### Model Loading Overhead (~14s)
- HeartMuLa weights: ~13s (289 shards at ~21.75 it/s avg)
- HeartCodec weights: ~6s (818 shards)
- Codec audio reconstruction: ~2s (10 refinement steps)

## Tags That Guided Male Vocal (verified working)

```text
piano love ballad,male vocal,male singer,deep male voice,intimate,tender,romantic,sensual,slow tempo
```

Note: Tags influence but don't guarantee vocal timbre. The `ref_audio` parameter is `NotImplemented`.

## Inference Command Template

### 60-second song (foreground safe, ~7.5 min, fits 600s timeout)
```bash
cd ~/heartlib && source .venv/bin/activate && PYTHONPATH=./src python examples/run_music_generation.py \
  --model_path ./ckpt \
  --lyrics ./assets/lyrics.txt \
  --tags ./assets/tags.txt \
  --save_path ./assets/song.wav \
  --mula_dtype float16 \
  --codec_dtype float16 \
  --lazy_load True \
  --max_audio_length_ms 60000 \
  --topk 50 \
  --temperature 1.0
```

### 90-second song (background required, ~10.5 min, exceeds 600s)
```bash
# Use background=true with notify_on_complete=true
```

## Model Loading Times

| Phase | Time | Notes |
|-------|------|-------|
| HeartMuLa weight load | ~13s | 289 safetensors shards |
| Generation (750 frames) | ~7m 20s | Average across normal + slow phases |
| HeartCodec weight load | ~6s | 818 safetensors shards |
| Audio reconstruction | ~2s | 10 refinement steps |
| **Total (60s song)** | **~7m 33s** | From invocation to .wav file |

## Memory Usage

- HeartMuLa active: ~6.2 GB VRAM
- HeartCodec active: ~3.1 GB VRAM
- With lazy_load=True, only one model in VRAM at a time
- Total peak: ~6.2 GB (HeartMuLa phase)
