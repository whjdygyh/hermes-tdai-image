# Evaluating AI-Generated Music — Audio Feature Analysis

**Use case:** You generated instrumental tracks (Suno/Stable Audio/Mureka) and need to evaluate which one suits a specific purpose (meditation, yoga, focus, background, dance, etc.) without being able to hear them.

**Method:** Extract audio features via `librosa` — spectral, temporal, and dynamic characteristics — then map them to suitability criteria.

---

## Quick Reference: Feature → Meaning

| Feature | What It Measures | Meditation Ideal | Dance/Upbeat Ideal |
|---------|-----------------|------------------|-------------------|
| **BPM (Tempo)** | Beats per minute | 60-120 (slow) | 120-180+ (fast) |
| **Spectral Centroid** | Brightness ("warm" = low, "bright" = high) | ≤1800 Hz (warm) | ≥2000 Hz (bright) |
| **Zero Crossing Rate (ZCR)** | How "busy/dense" the sound is | ≤0.025 (sparse) | ≥0.03 (busy) |
| **RMS Mean** | Average loudness | ≤0.15 (quiet) | ≥0.18 (loud) |
| **RMS Std** | Dynamic variation | Moderate (0.03-0.05) | Higher variation |
| **Silent Ratio** | Fraction of near-silent moments | Higher = more breathing room | Lower = continuous energy |
| **Spectral Flatness** | Noise vs pure-tone quality | ≤0.005 (tonal/pure) | Higher = noisier/harsher |
| **Onset Strength Mean** | Percussiveness/attack energy | ≤1.2 (gentle) | ≥1.5 (driving) |

---

## Extraction Script (Python)

```python
import librosa
import numpy as np

def analyze_track(filepath):
    y, sr = librosa.load(filepath, sr=None, mono=True)
    dur = librosa.get_duration(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    spec_cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    spec_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    rms = float(np.mean(librosa.feature.rms(y=y)))
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    
    # Dynamic features (2-sec windows, 0.5-sec hops)
    frame_len = int(sr * 2)
    hop_len = int(sr * 0.5)
    rms_frames = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    silent_ratio = float(np.sum(rms_frames < (np.mean(rms_frames) * 0.1)) / len(rms_frames))
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # MFCC (timbral fingerprint)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    return {
        "duration_s": round(dur, 1),
        "bpm": round(float(tempo)),
        "spectral_centroid_hz": round(spec_cent),
        "zcr": round(zcr, 4),
        "rms_mean": round(float(np.mean(rms_frames)), 6),
        "rms_std": round(float(np.std(rms_frames)), 6),
        "silent_ratio": round(silent_ratio, 3),
        "spectral_flatness": round(flatness, 4),
        "onset_mean": round(float(np.mean(onset_env)), 4),
        "onset_std": round(float(np.std(onset_env)), 4),
        "mfcc_mean": [round(float(x), 1) for x in np.mean(mfccs, axis=1)[:6]],
    }
```

---

## Meditation Suitability Score

Composite formula that maps audio features to a 1-10 scale:

```python
def meditation_score(track):
    score = (
        -0.3 * min(track["bpm"] / 100, 2.0)    # slower = better
        - 0.3 * min(track["zcr"] * 100, 3.0)   # less busy = better
        - 0.2 * min(track["rms_mean"] * 100, 3.0)  # quieter = better
        + 0.1 * track["spectral_flatness"]      # more tonal = better
        - 0.2 * min(track["spectral_centroid_hz"] / 2000, 2.0)  # warmer = better
    )
    return max(1, min(10, 5 + score * 2))
```

**Interpretation:**
| Score | Meaning |
|-------|---------|
| 8-10 | Excellent meditation track — warm, slow, gentle |
| 6-7 | Good background/ambient — decent but not ideal |
| 4-5 | Neutral — could work for focus or casual listening |
| 1-3 | Not meditation — too fast/bright/dynamic |

---

## Use-Case Scoring Profiles

| Use Case | Key Priority | Watch Out For |
|----------|-------------|---------------|
| **Meditation** | Low BPM, warm centroid, low ZCR, low onset | High BPM >150, bright >2kHz centroid |
| **Yoga Flow** | Moderate BPM (100-130), moderate onset | Too slow (<80 BPM = lethargic) |
| **Deep Focus** | Low onset, mid-range centroid, medium BPM | Percussive elements, high ZCR |
| **Background Ambient** | Low RMS, high silent ratio, very flat dynamics | Loud passages, sudden changes |
| **Upbeat/Dance** | High BPM >130, high onset, bright centroid | Low energy, sparse texture |

---

## Concrete Example: Bansuri Meditation Tracks

Four variations of "Moon Over Varanasi" were evaluated (Suno-generated Bansuri pieces):

| Track | BPM | Spec. Centroid | ZCR | RMS | Flatness | Onset | **Meditation** |
|-------|-----|---------------|-----|-----|----------|-------|:------------:|
| 1 | 170 | 1813 Hz | 0.026 | 0.152 | 0.0002 | 1.22 | ⭐⭐ |
| 2 | 120 | 2006 Hz | 0.028 | 0.159 | 0.0084 | 1.16 | ⭐⭐⭐⭐ |
| **3** | **137** | **1692 Hz** | **0.023** | **0.149** | **0.0022** | **1.14** | **⭐⭐⭐⭐⭐** |
| 4 | 176 | 1739 Hz | 0.025 | 0.160 | 0.0016 | 1.31 | ⭐ |

**Winner: Track 3** — Warmest tone (1692 Hz), quietest/gentlest (lowest RMS 0.149, lowest ZCR 0.023, lowest onset 1.14), highly tonal. Perfect for deep meditation.

---

## Pitfalls

- **BPM detection can be unreliable** on ambient/sparse tracks. Cross-check with onset regularity.
- **MP3 compression** can slightly alter spectral features. Prefer WAV for analysis.
- **Long intros/outros** (silence/fade) can skew RMS mean — trim first/last 5 seconds if needed.
- **Stereo vs mono**: librosa.load() with mono=True by default. Be consistent across comparisons.
- **Sample rate**: librosa auto-resamples to 22050 Hz by default. Use `sr=None` to keep original rate.
