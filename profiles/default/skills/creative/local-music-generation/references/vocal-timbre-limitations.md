# HeartMuLa Vocal Timbre Limitations (实测 2026-05-13/14/14_2)

## 核心结论

**HeartMuLa 没有任何音色/声线/性别控制参数。** 生成的人声是模型随机决定的，用户无法指定男声/女声。
**此结论为代码级确认，不是推测。**

## 代码考古：ref_audio 存在但被禁用

在 `src/heartlib/pipelines/music_generation.py` 中，`preprocess` 方法（第221-225行）：

```python
# process reference audio
ref_audio = inputs.get("ref_audio", None)
if ref_audio is not None:
    raise NotImplementedError("ref_audio is not supported yet.")
muq_embed = torch.zeros([self._muq_dim], dtype=self.mula_dtype)
```

- `ref_audio` 参数**明确存在** — 设计上就是用来传入参考音频来控制歌声音色的（类似RVC/so-vits-svc的声线克隆）
- 但被**硬编码的 `NotImplementedError` 禁用** — 不是"可能不支持"，是作者明确写着"还没实现"
- `muq_embed` 被设为全零张量 — 说明没有参考音频的特征嵌入

**结论：HeartMuLa的音色控制（如果以后实现）会通过参考音频来实现，但当前版本完全不支持。**

## 实测过程

### 第一次生成 (2026-05-13)
- 参数: `temperature=1.0, topk=50, cfg_scale=1.5`
- 歌词: 《Every Day the Light Returns》英文
- 标签: `piano,happy`
- 结果: **女声** — 用户反馈"为什么是个女人"

### 第二次生成 (2026-05-14)
- 参数: `temperature=1.2, topk=50, cfg_scale=1.5`
- 标签: `piano,happy`
- 结果: **推测仍为女声** — 用户未提供明确反馈，但根据"我觉得你没研究明白"推断仍不满意

### 第三次生成 (2026-05-14_2) — Tags关键词尝试
- 参数: `temperature=1.0, topk=50, cfg_scale=1.5`
- 标签: **`piano,happy,male vocal,male singer,deep male voice`**
- 结果: **女声** — 用户反馈"女的"
- **结论：Tags中的声线关键词完全无效** — 模型不理解或不遵循 `male vocal` 这类标签来控制歌手性别

### 第四次~第六次生成 (2026-05-14) — 参数全范围扫描，均失败
用户要求生成一首pop love song，尝试了**3种完全不同的参数组合**：

| 版本 | temperature | topk | cfg_scale | tags (男声引导) | 结果 |
|------|------------|------|-----------|-----------------|------|
| V1 | 1.0 | 50 | 1.5 | `male vocal,male singer,deep male voice,romantic...` | ❌ 女声 |
| V2 | **0.8** | **30** | **2.0** | 同上 + `male vocal only,baritone,masculine vocal,not female` | ❌ 女声 |
| V3 | **1.2** | **80** | **2.5** | 同上 + `husky male voice,low pitch` | ❌ 女声 |

**结论：无论怎么调参（低温度+高cfg压随机性，或高温度+高topk+高cfg扩搜索+强标签约束），模型始终输出女声。参数对声线性别的影响为零。**

### HeartMuLa-RL-oss-3B-20260123 尝试 (2026-05-14) — 进行中
- RL微调版，README称"更精准的风格和标签控制"
- 同一架构（3B参数，4分片），预计VRAM占用与oss-3B相同 (~3.1GB float16)
- 是否真正改善tags对声线的控制**尚未验证**
- 下载方式：`HF_ENDPOINT=https://hf-mirror.com huggingface-cli download HeartMuLa/HeartMuLa-RL-oss-3B-20260123 --local-dir ckpt/HeartMuLa-RL-oss-3B-20260123 --local-dir-use-symlinks False`
- 运行方式与oss-3B相同，只需改 `--model_path` 参数

### 7B内部版 — 未开源
- README提到："Our latest internal version of HeartMuLa-7B achieves comparable performance with Suno"
- **该版本未开源**，HuggingFace上仅有3B版本（oss-3B, oss-3B-happy-new-year, RL-oss-3B-20260123）
- 仅在HeartMuLa的HF Spaces在线Demo中使用
- 无需继续寻找7B权重

## Tags关键词无效的推测原因

HeartMuLa的标签系统是设计用来说明音乐风格（piano, rock, happy, sad）和乐器（guitar, drums, synthesizer）的，**不是**用来指定歌手特征的。训练数据中的声线信息可能没有作为标签编码，或者即使有少量的"male vocal"标签，模型也没有学到将其映射到特定声线输出上。

## 流程反思：不要先试再查

2026-05-14_2 用户明确纠正："我觉得你没研究明白，好好查查资料，说明书啥的"

**正确的流程应该是：**
1. 先读源码，确认模型是否有声线控制参数
2. 确认 `ref_audio` 的参数状态
3. 确认tags的设计用途
4. **然后再跟用户汇报结论**，而不是先跑实验碰运气

用户反复强调"角本执行肯定前后文连不起来的"——不研究就试的"试错法"在AI伴侣场景下会让用户觉得你不了解她/他。

## TTS 与 唱歌 的区别（用户明确纠正）

- **TTS (edge-tts / volcengine)**: 只能朗读/阅读（reading/recitation），不能真正唱歌
  - 用户原话: "你用阿虎只能是阅读，又不能唱歌"
  - TTS朗读歌词听起来像念白，没有旋律和节奏
- **AI音乐生成模型 (HeartMuLa / Suno)**: 生成的歌声有旋律，但声线不可控
- 如果用户要求"听你唱歌"且只有TTS可用，需要说明TTS只能朗读而非唱歌
