# SenseVoice Test Results — 2026-05-18

## Environment
- WSL2 (Ubuntu 22.04)
- GPU: NVIDIA RTX 3060 Ti (8GB VRAM)
- Python: 3.10
- CUDA: 13.0 (torch 2.11.0+cu130)
- funasr: 1.3.1
- torchaudio: 2.11.0+cu130
- modelscope: 1.36.1

## Download
- Model: `iic/SenseVoiceSmall` from ModelScope
- Size: 893MB (model.pt) + ~50KB metadata files
- Download time: 1min 28s
- Cache: `~/.cache/modelscope/hub/models/iic/SenseVoiceSmall/`
- 19 files total

## Inference Test — Chinese example

**Input**: `zh.mp3` (included with model, ~45KB, ~5s of Mandarin speech)
**Prompt**: "开放时间早上9点至下午5点。"

### Raw output
```
<|zh|><|NEUTRAL|><|Speech|><|withitn|>开放时间早上9点至下午5点。
```

### Parsed metadata
- Language: zh (Chinese) ✓
- Emotion: NEUTRAL (neutral) ✓
- Event: Speech (not music/noise) ✓
- ITN: withitn (inverse text normalization applied — 9点 not 九点)

### Performance
- Model load: 11.3s (first time)
- Inference: 1.09s
- RTF: 0.178 (5.6× real-time)

## Verdict
✅ Pipeline confirmed working. Architecture decision (2026-05-18): CosyVoice deferred — choosing 纯听模式 instead (SenseVoice → Edge TTS). See `mlops/local-voice-pipeline` for full rationale.
