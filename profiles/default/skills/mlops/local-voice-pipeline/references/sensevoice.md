# SenseVoice — Detailed Component Reference

Model from FunAudioLLM (Alibaba DAMO Academy). Multilingual ASR with built-in emotion recognition and audio event detection. Outperforms Whisper on Chinese and 50+ languages, 15× faster than Whisper-Large.

## When to Use

- **Chinese ASR** — significantly outperforms Whisper on Mandarin and Cantonese
- **Emotion detection needed** — outputs NEUTRAL/HAPPY/SAD/ANGRY/FEARFUL/SURPRISE labels
- **Event detection** — detects laughter, applause, crying, coughing, sneezing, music
- **Real-time pipeline** — RTF 0.178 on RTX 3060 Ti (10s audio in ~1.78s)
- **Low-latency** — non-autoregressive end-to-end framework, 70ms per 10s audio

**Use Whisper instead when**: English-only, need speaker diarization, or hardware-constrained (<6GB VRAM)

## Model Info

- **SenseVoiceSmall**: 893MB, ~4-5GB VRAM at inference
- Trained on 400k+ hours of multilingual data
- Output format: `<lang_tag><emotion><event><itn_tag>transcribed_text`

## Quick Start (WSL + CUDA)

### 1. Install dependencies

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
pip install -U funasr torchaudio modelscope
```

**Important**: Use ModelScope (not HuggingFace) for download — much faster for Chinese models on mainland networks.

### 2. Download model

```python
from modelscope.hub.snapshot_download import snapshot_download
model_dir = snapshot_download('iic/SenseVoiceSmall')
# → ~/.cache/modelscope/hub/models/iic/SenseVoiceSmall/
# ~893MB download
```

### 3. Load and infer

```python
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

model = AutoModel(
    model='iic/SenseVoiceSmall',
    device='cuda:0',
    disable_update=True,
)

res = model.generate(
    input='audio.mp3',
    cache={},
    language='zh',     # or 'auto', 'en', 'ja', 'ko', 'yue'
    use_itn=True,      # inverse text normalization (numbers/dates/prices)
    batch_size_s=60,
)

# Raw output includes metadata tags
print(res[0]['text'])
# e.g. <|zh|><|NEUTRAL|><|Speech|><|withitn|>开放时间早上9点至下午5点。

# Clean post-processed text
text = rich_transcription_postprocess(res[0]['text'])
print(text)
# 开放时间早上9点至下午5点。
```

## Output Format

The raw text output includes 4 metadata tags delimited by `|<>|`:

```
<|LANG|><|EMOTION|><|EVENT|><|ITN|>transcribed_content
```

| Tag | Values | Meaning |
|-----|--------|---------|
| LANG | zh, en, ja, ko, yue, etc. | Detected language |
| EMOTION | NEUTRAL, HAPPY, SAD, ANGRY, FEARFUL, SURPRISE | Emotion classification |
| EVENT | Speech, Music, Laughter, Applause, Cry, Cough, Sneeze | Audio event type |
| ITN | withitn, withoutitn | Whether ITN was applied |

## Performance (RTX 3060 Ti 8GB)

| Metric | Value |
|--------|-------|
| Model load time | ~11s (first time) |
| Inference (zh.mp3, ~5s audio) | ~1.09s |
| RTF | 0.178 (5.6× real-time) |
| VRAM usage | ~4-5GB |

## Language Support

- **Best quality**: Chinese (Mandarin), Cantonese, English, Japanese, Korean
- **Good quality**: 50+ languages supported
- Built-in language identification per utterance

## Pitfalls

- **First load slow** — model downloads from ModelScope and loads into VRAM (~11s)
- **funasr must be >= 1.0** — older versions have API incompatibilities
- **torchaudio required** — not auto-installed with funasr
- **ModelScope cache location** — `~/.cache/modelscope/hub/models/iic/SenseVoiceSmall/` (not HF cache)
- **VRAM** — runs comfortably on 8GB GPU (RTX 3060 Ti), do NOT also run SD or LLM inference concurrently
- **No streaming** — designed for batch inference (non-autoregressive), not real-time streaming ASR

## Pipeline Integration

SenseVoice is the **ASR** component in the voice pipeline. See the umbrella skill `local-voice-pipeline` for full architecture guidance and component selection.

### Recommended pipeline (纯听模式 on 8GB GPU):
```
Mic/File → SenseVoiceSmall (ASR+emotion) → Local LLM (understanding) → Edge TTS (speak)
```

### CosyVoice integration:
For a full local loop (SenseVoice + CosyVoice), VRAM budget is tight on 8GB:
- SenseVoiceSmall: ~4-5 GB
- CosyVoice-300M: ~1-2 GB extra
- Total: ~6-7 GB — no room for separate LLM

**Prefer 纯听模式** unless you have >10GB VRAM or can unload models between stages.
