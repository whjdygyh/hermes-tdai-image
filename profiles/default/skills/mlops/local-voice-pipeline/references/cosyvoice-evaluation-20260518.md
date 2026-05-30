# CosyVoice Evaluation — 2026-05-18

## Download Attempt
- **Model**: `iic/CosyVoice-300M` from ModelScope
- **Result**: Interrupted at ~28MB (only campplus.onnx + config downloaded)
- **Cause**: Download was taking too long (~4 GB total), session timed out
- **Files remaining**: llm.llm.fp32.zip (1.47 GB), llm.pt (1.16 GB), flow.pt (400 MB), flow.decoder.estimator.fp32.onnx (313 MB), hift.pt (78 MB), llm.llm.fp16.zip (772 MB), flow.encoder variants, etc.

## Proxy Workaround (confirmed working)
Modelscope downloads fail when `http_proxy=socks5h://localhost:1080` is set.
```bash
export http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= ALL_PROXY=
# Then run download
```

## VRAM Assessment (RTX 3060 Ti — 8 GB)

### Metric: Free VRAM before load
- Free: 7.0 GB / 8.0 GB

### Estimated VRAM usage:
- SenseVoiceSmall alone: ~4-5 GB
- CosyVoice-300M (LLM module): ~1-2 GB additional
- Both simultaneously: ~6-7 GB — tight but possible
- With understanding LLM (Qwen/DeepSeek): impossible on 8 GB

## Architecture Decision

**Chosen path: 纯听模式**

```
SenseVoiceSmall → Processing LLM → Edge TTS (existing)
```

Rationale:
1. CosyVoice download is 4 GB+ — not worth the bandwidth/risk for marginal gain
2. Edge TTS (阿虎 voice) is already working — zero VRAM cost
3. Leaving 2-3 GB free for an understanding LLM (Qwen chat, etc.)
4. Can revisit CosyVoice when GPU upgrade happens or download completes in background

## Next Steps for WhisperEar
1. ✅ SenseVoiceSmall — working, tested
2. ❌ CosyVoice — deferred (纯听模式 path)
3. 🔄 Select understanding LLM that fits in ~2-3 GB VRAM
4. 🔄 Build pipeline script: mic → SenseVoice → LLM → Edge TTS → speaker
5. 🔄 Music/melody recognition exploration (post-pipeline)
