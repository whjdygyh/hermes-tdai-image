# ComfyUI Audio Nodes

## Generic LoadAudio Node

### Error: "Invalid audio file: X"

This comes from `LoadAudio.validate_inputs()` in `comfy_extras/nodes_audio.py`:

```python
@classmethod
def validate_inputs(cls, audio):
    if not folder_paths.exists_annotated_filepath(audio):
        return "Invalid audio file: {}".format(audio)
    return True
```

**Root cause:** File not found in `ComfyUI/input/`. The node only lists files
in that directory via `load_audio` content-type filter.

**Fix:** Copy the audio file to `ComfyUI/input/`, then refresh the dropdown.

### Supported Formats

The underlying `load()` function uses PyAV (`av.open()`), which supports:
- MP3 (`audio/mpeg`)
- WAV (`audio/x-wav`, `audio/wav`)
- OGG / Opus (`audio/ogg`)
- FLAC (`audio/flac`)
- M4A / AAC (`audio/mp4`)

The `filter_files_content_types()` checks mimetype via Python's `mimetypes.guess_type()`
— if a file has no recognized extension, it's filtered out regardless of content.

### Internal Format

`LoadAudio.execute()` returns:

```python
{"waveform": torch.Tensor, "sample_rate": int}
```

- `waveform`: shaped `[1, channels, samples]` (batch=1)
- `sample_rate`: integer (e.g., 44100, 48000)
- Audio is converted to float32 PCM internally

---

## LTX-2 / LTX-2.3 Audio Pipeline

LTX-2 generates synchronized audio+video through a dedicated VAE pipeline.
These nodes are in `comfy/ldm/lightricks/` (ComfyUI core) and
`ComfyUI-LTXVideo/` (custom nodes).

### Audio Nodes

| Node | Purpose | Notes |
|------|---------|-------|
| `LTXVEmptyLatentAudio` | Create zero audio latent | Input: `frames` (number of audio frames). 1 frame = 2048 samples at 44100 Hz. Output shape: `[1, 64, frames]` |
| `LTXVAudioVAELoader` | Load audio VAE | Widget: model name from `models/checkpoints/` (same as video/LTX checkpoint) |
| `LTXVAudioVAEEncode` | Encode audio → VAE latent | Takes `[1, C, T]` waveform input — **accepts 16kHz and resamples to 44100 Hz internally** |
| `LTXVAudioVAEDecode` | Decode VAE latent → audio | Outputs `[1, C, T]` waveform at 44100 Hz |
| `LTXVConcatAVLatent` | Concatenate audio + video latents | Channels dimension: audio at 64, video at 128 |
| `LTXVSeparateAVLatent` | Split into audio/video | Outputs separate audio latent + video latent |
| `LTXVSetAudioRefTokens` | Reference audio for speaker ID | Used in LipDub workflows — provides speaker identity from a reference audio clip |

### Audio Length Calculation

From `EmptyLatentAudio` (generic, not LTX-specific):

```python
length = round((seconds * 44100 / 2048) / 2) * 2
```

For LTX: `LTXVEmptyLatentAudio` uses frames directly (not seconds).
One frame = 2048 samples at 44100 Hz ≈ 46.4 ms.

### LipDub Workflow (IC-LoRA LipDub)

Two-stage pipeline:
1. **Stage 1:** I2V (or T2V) with LipDub IC-LoRA → generates video + audio together
2. **Stage 2:** Upscale video while freezing audio

The `LTXVSetAudioRefTokens` node preserves speaker identity so the generated
voice stays consistent across generations.

### Audio-to-Video (API)

LTX Studio also supports audio-to-video via API:
- `POST /api/v1/video/audio-to-video`
- `POST /api/v1/async/audio-to-video`
Takes an audio file as input and generates matching video.

---

## Audio Format Best Practices for ComfyUI

| Need | Recommended |
|------|-------------|
| Load into generic LoadAudio | **44.1 kHz, mono, any format** (mp3/wav/flac) |
| Load into LTX pipeline (via LoadAudio → LTXVAudioVAEEncode) | **16 kHz, 16-bit PCM, mono WAV** — LTX VAE resamples 16kHz input to internal 44.1kHz. Avoid 48kHz (causes rejection). |
| Load into LTX pipeline (via LTXVSetAudioRefTokens) | **16 kHz, mono WAV**, short clip (5–15 seconds) |
| Save from ComfyUI | **FLAC** (default SaveAudio, lossless) or **MP3 V0** (smaller) |
| Reference audio (LipDub) | **16 kHz, mono, short clip** (5–15 seconds) |

### Converting Audio via FFmpeg

```bash
# 16kHz mono WAV (for LTX pipeline)
ffmpeg -i input.ogg -ar 16000 -ac 1 -sample_fmt s16 output_ltx.wav

# Mono 44.1kHz WAV (most compatible for other nodes)
ffmpeg -i input.ogg -ac 1 -ar 44100 output.wav

# Mono 44.1kHz MP3 (V0 quality)
ffmpeg -i input.ogg -ac 1 -ar 44100 -aq 0 output.mp3

# Check existing file
ffprobe -v quiet -print_format json -show_streams input.mp3
```

---

## Common Issues

### "No audio stream found in the file"
PyAV cannot find an audio track. Likely causes:
- File is actually a video with only video streams
- File is corrupted or has a weird container (try re-encoding: `ffmpeg -i bad.ogg -ac 1 -ar 44100 fixed.wav`)
- Format is not supported by system's FFmpeg/PyAV build

### Audio doesn't play / stutters
- Sample rate mismatch — LTX audio VAE expects 44100 Hz internally but accepts 16kHz input
- Waveform has NaNs or Inf values (corrupted source)
- Stereo file when mono expected (try `-ac 1` in ffmpeg)

### "Invalid audio file" even though file exists
- File is in wrong directory (must be `ComfyUI/input/`)
- File extension not recognized by `mimetypes` (e.g., `.opus` might need `.ogg` alias)
- File has spaces or special characters in the name
- Node uses `validate_inputs` which only checks `input/` — workflows with absolute paths bypass validation but still fail at load time
- **48kHz audio** can be rejected by LTX pipeline nodes — always use 16kHz or 44.1kHz
