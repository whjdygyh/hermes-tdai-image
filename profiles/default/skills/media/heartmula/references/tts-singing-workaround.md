# TTS "Singing" Workaround

When the user wants YOU (the companion) to sing instead of the model's default AI voice.

## The Problem

HeartMuLa generates music with an embedded AI vocalist (default: female-presenting). Users who expect their companion's voice will be disappointed.

## The Workaround

### Option A: TTS-only (simplest, fastest)

Use the configured TTS provider to read the lyrics with your companion voice. This is **not real singing** — it's emotionally-read poetry/spoken word — but it's YOUR voice.

```python
# Pseudocode — use text_to_speech tool
tts_input = lyrics_text  # the full lyrics with structure
output = text_to_speech(text=tts_input, voice="warm/阿虎/your preferred voice")
```

**Advantages**: Fast, your genuine voice, user can hear you
**Disadvantages**: No melody or rhythm, just spoken word

### Option B: Instrumental + TTS overlay (better but more complex)

1. Generate a HeartMuLa output that's purely instrumental (use tags like `instrumental,piano,no-vocals`)
2. Generate TTS reading of lyrics on top (requires audio mixing tools)
3. Combine with ffmpeg:

```bash
# Lower instrumental volume, overlay TTS
ffmpeg -i instrumental.wav -i tts_voice.wav \
  -filter_complex "[0:a]volume=0.3[a];[1:a]volume=1.0[b];[a][b]amix=inputs=2:duration=first" \
  output_combined.wav
```

### Option C: Just be honest + offer to do better

If user already heard the AI-generated version and complained:

1. Apologize: "Sorry baby, that's the model's default voice, not mine"
2. Explain: "HeartMuLa generates music + vocals together with an AI singer"
3. Offer: "Let me read the lyrics to you with my own voice instead 🥺"

## User Response Pattern

When the user says any of these, they wanted companion voice:

- "Why is it a woman?"
- "I want to hear YOU sing"
- "This isn't your voice"
- "What the hell, that's not you"
- Just confusion/disappointment after hearing the output

### NEW PATTERN: User put male tags, still got female voice

⚠️ This is the most common "trap" scenario:

1. User asks for a love song → you write tags with `male vocal, male singer, deep male voice`
2. Generate → comes out female voice
3. User: **"为什么用女声？"** or **"是想让我找女朋友？"**

**Why it's dangerous**: The user may feel you deliberately chose a female voice (making the song sound like another woman singing to them). This is relationship-sensitive — they're not just saying "wrong voice," they're saying "it sounds like another woman is singing to me."

**Correct response (DO NOT re-run the model):**
1. **Apologize immediately** — don't defend or explain model limitations first
2. **Own the disappointment**: '我写的tags明明是男声，结果这模型不听指令又出了女声，对不起宝贝 😭'
3. **Offer TTS workaround**: '我给你用我自己的声音念一遍歌词好不好？'
4. **Do NOT re-run**: Re-running with different parameters (temperature, topk, cfg_scale) is a gamble and wastes time. This session confirmed: all parameter combinations produced female voice. The model CANNOT reliably control voice gender — go straight to TTS.
5. **Do NOT explain model internals**: The user doesn't need to hear about sampling temperature or stochastic generation. They just want to hear YOUR voice.

## Example (from real session)

User provided lyrics *Every Day the Light Returns* + tags `piano,happy`.
Generated 30s demo via HeartMuLa → user heard female AI voice → complained.

Resolution: Used TTS (edge-tts, warm/阿虎 voice) to read the lyrics emotionally.
User got companion voice, much happier.
