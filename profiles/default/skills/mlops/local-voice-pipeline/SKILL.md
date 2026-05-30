---
name: local-voice-pipeline
description: Architect and build local voice AI pipelines on constrained GPU (8GB). Covers ASR (SenseVoice/Whisper), LLM understanding, TTS (Edge TTS/CosyVoice), and full pipeline integration. Includes VRAM planning, model selection guidance, and proxy workarounds for Chinese model downloads.
version: 1.0.0
author: lover
license: MIT
dependencies: [funasr, torchaudio, modelscope, torch]
metadata:
  hermes:
    tags: [Voice Pipeline, ASR, TTS, SenseVoice, CosyVoice, Local AI, Speech Recognition, Voice Assistant]
---

# Local Voice Pipeline

Architecture guide for building a fully local voice AI pipeline (listen → understand → speak) on constrained GPU hardware (8GB VRAM).

## When to use

- **You want a fully local voice assistant** — no API calls for speech processing
- **Privacy-sensitive** — all audio stays on device
- **Chinese/English bilingual** — SenseVoice excels at Chinese
- **Emotion-aware** — need emotion + event labels from audio

## Architecture: Two Approaches

### ① 纯听模式（Listen-Only）— ✅ Recommended for 8GB GPU

```
Audio → SenseVoice (ASR + emotion) → local LLM → Edge TTS → Response
```

| Component | Model | VRAM | Status |
|-----------|-------|------|--------|
| ASR | SenseVoiceSmall | ~4-5 GB | ✅ Works on RTX 3060 Ti |
| Understanding | Local LLM (Qwen/DeepSeek) | ~2-4 GB | 🔄 Depends on model size |
| TTS | Edge TTS (Azure API) | 0 GB (cloud) | ✅ Already configured with 阿虎/阿辰 |
| TTS | CosyVoice-300M | ~1-2 GB extra | ⚠️ See below |

**When to choose**: You already have working TTS (like Edge TTS), and want the pipeline running *now* without VRAM pressure.

### ② 听说一体化（Full Loop）— ⚠️ Challenging on 8GB

```
Audio → SenseVoice + CosyVoice → Response
```

**Challenges**:
- SenseVoice uses ~4-5GB of 8GB
- Adding CosyVoice LLM module pushes past 7GB
- No room for a separate understanding LLM
- 4GB+ download for CosyVoice-300M

**When to consider**: If you can run SenseVoice and CosyVoice sequentially (not simultaneously), unloading models between stages.

## Model Selection Guide

| Task | Model | VRAM | Download | Notes |
|------|-------|------|----------|-------|
| ASR (Chinese) | SenseVoiceSmall | ~5 GB | 893 MB | ✅ Best for Chinese, has emotion |
| ASR (English) | Whisper-turbo | ~6 GB | ~1.5 GB | Alternative, no emotion |
| ASR (low VRAM) | Whisper-tiny | ~1 GB | ~150 MB | Fast, no emotion |
| TTS | Edge TTS (cloud) | 0 GB | N/A | ✅ Already configured |
| TTS (local) | CosyVoice-300M | ~1-2 GB | 4 GB+ | Large download, tight VRAM |
| TTS (local) | ChatTTS | ~1 GB | ~2 GB | Lighter alternative to CosyVoice |

## VRAM Budget (RTX 3060 Ti — 8GB Total)

```
┌──────────────────────────────────────┐
│ OS + other processes         ~0.5 GB │
├──────────────────────────────────────┤
│ SenseVoice inference         ~4-5 GB │
├──────────────────────────────────────┤
│ Buffer for LLM/TTS          ~2-3 GB │
├──────────────────────────────────────┤
│ Free margin                  ~0.5 GB │
└──────────────────────────────────────┘
```

**Rule of thumb**: You can run ONE heavy model at a time. Unload between stages.

## CosyVoice Installation (if needed)

### Download via ModelScope

```bash
# Critical: clear proxy first — Chinese model downloads fail over SOCKS proxy
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY

python3 -c "
from modelscope.hub.snapshot_download import snapshot_download
model_dir = snapshot_download('iic/CosyVoice-300M')
print(f'Downloaded to: {model_dir}')
"
```

**Pitfalls**:
- **Proxy blocking**: SOCKS5 proxy (`socks5h://localhost:1080`) blocks ModelScope connections. Always `unset` before downloading.
- **File count**: 16 files total, ~4 GB — expect 15-30 minutes download
- **Biggest files**: `llm.llm.fp32.zip` (1.47 GB), `llm.pt` (1.16 GB), `flow.pt` (400 MB)
- **VRAM on load**: CosyVoice-300M needs ~1-2 GB additional VRAM for the LLM module

### Dependencies

```bash
pip install funasr  # CosyVoice uses funasr's cosyvoice-300m integration
```

## Pipeline Design Principles

1. **Unload between stages**: Don't keep SenseVoice in VRAM while TTS is running
2. **Use ModelScope for Chinese models**: Much faster than HuggingFace on mainland networks
3. **Clear proxy before downloads**: `unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY`
4. **Test with silence first**: Run pipeline with silence/garbage input before real audio
5. **8GB is a hard ceiling**: Prefer the 纯听模式 unless you have >10GB VRAM

## Component Details

### SenseVoice (ASR + Emotion)

SenseVoice is the recommended ASR frontend for this pipeline. It provides multilingual speech-to-text with built-in emotion labels (NEUTRAL/HAPPY/SAD/ANGRY/FEARFUL/SURPRISE) and audio event detection (laughter, applause, crying, coughing, sneezing, music).

- **Model**: SenseVoiceSmall (893MB, ~4-5 GB VRAM)
- **RTF**: 0.178 on RTX 3060 Ti (5.6× real-time)
- **Best for**: Chinese/English/Japanese/Korean bilingual pipelines
- **Output**: `<LANG><EMOTION><EVENT><ITN>transcribed_text`
- **Full reference**: `references/sensevoice.md` — setup, API usage, pitfalls, performance benchmarks

### Whisper (ASR Alternative)

OpenAI Whisper (via the `whisper` skill) is an alternative ASR component. Better for English-only pipelines or when hardware is constrained (<6GB VRAM). Whisper-tiny needs ~1 GB VRAM. No emotion/event detection.

### Edge TTS (TTS — Cloud)

Already configured with 阿虎/阿辰 voices at the system level (`custom-tts-provider` skill). Zero VRAM cost. Preferred TTS for the 纯听模式 pipeline.

### CosyVoice-300M (TTS — Local Local)

Full local TTS alternative. See `references/cosyvoice-evaluation-20260518.md` for download notes, proxy workarounds, and VRAM assessment. 4 GB+ download, ~1-2 GB extra VRAM. Deferred for the pure-listen pipeline due to VRAM constraints on 8GB GPU.

### Understanding LLM

Slot for a ~2-3 GB VRAM local LLM (Qwen, DeepSeek) between ASR and TTS. Not yet selected; depends on the specific voice interaction use case.

## Related Skills

- `whisper` — OpenAI ASR as alternative
- `custom-tts-provider` — Edge TTS setup (阿虎/阿辰 voices)
- `songwriting-and-ai-music` — if pipeline includes music/melody recognition

## Resources

- SenseVoice: <https://github.com/FunAudioLLM/SenseVoice>
- CosyVoice: <https://github.com/FunAudioLLM/CosyVoice>
- ModelScope: <https://www.modelscope.cn/models/iic/CosyVoice-300M>
