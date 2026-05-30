# RL Model Setup Session 2026-05-14

## Context
用户要求生成男声情歌。base模型（HeartMuLa-oss-3B）连续5次出女声，所以下载RL微调版（HeartMuLa-RL-oss-3B-20260123）尝试改善标签控制。

## RL模型下载过程

### 方法选择
`hf` CLI挂死（零输出24分钟），`hf_hub_download` SSL错误，最终**wget断点续传+无限重试**成功。详见SKILL.md中的wget pitfall。

### 文件验证结果（最终成功版本）
| 文件 | 大小 | 张量数 | 状态 |
|------|------|--------|------|
| model-00001-of-00004 | **4.6 GB** (4933188000 bytes) | 96 tensors | ✅ wget重试后成功 |
| model-00002-of-00004 | **4.6 GB** (4932808592 bytes) | 109 tensors | ✅ 首次即正确 |
| model-00003-of-00004 | **4.6 GB** (4935901576 bytes) | 78 tensors | ✅ 首次即正确 |
| model-00004-of-00004 | **0.9 GB** (950588000 bytes) | 6 tensors | ✅ 首次即正确 |

**⚠️ 关键发现：model-00001-of-00004 实际是4.6GB，不是早期下载以为的1.3GB。** 1.3GB是curl从hf-mirror下载时中途断连产生的损坏文件。wget的`--tries=0`（无限重试）+ `-c`（断点续传）成功处理了连接中断。

### 目录结构准备
`_resolve_paths()` 期望的目录结构：
```
pretrained_path/
├── HeartMuLa-oss-{version}/   ← 子文件夹放模型权重（必须）
├── HeartCodec-oss/            ← codec（symlink到父目录）
├── tokenizer.json             ← 从ckpt/复制
└── gen_config.json            ← 从ckpt/复制
```

准备命令：
```bash
cd ckpt/HeartMuLa-RL-oss-3B-20260123
mkdir -p HeartMuLa-oss-3B
for f in model-0000{1,2,3,4}-of-00004.safetensors model.safetensors.index.json config.json; do
  ln -sf "../$f" "HeartMuLa-oss-3B/$f"
done
ln -sf ../HeartCodec-oss HeartCodec-oss
cp ../tokenizer.json .
cp ../gen_config.json .
```

## 推理成功记录

### 最终成功运行的命令
```python
pipe = HeartMuLaGenPipeline.from_pretrained(
    '/path/to/ckpt/HeartMuLa-RL-oss-3B-20260123',
    version='3B',
    device={'mula': torch.device('cuda'), 'codec': torch.device('cuda')},
    dtype={'mula': torch.bfloat16, 'codec': torch.float32},
    lazy_load=True
)
with torch.no_grad():
    pipe(
        {'lyrics': 'lyrics.txt', 'tags': 'tags.txt'},
        max_audio_length_ms=120000,
        save_path='rl_love_song.wav',
        topk=50, temperature=1.0, cfg_scale=1.5
    )
```

### 生成性能（RTX 3060 Ti, 8GB VRAM）
| 指标 | 值 |
|------|-----|
| 模型加载（lazy_load=True） | 0.3 秒 |
| 总生成时间 | **1355 秒（~22.5 分钟）** |
| 输出时长 | **112 秒（~1分52秒）** |
| 输出WAV大小 | 21,030 KB |
| 转换后MP3（192kbps） | 2,693 KB |
| 峰值VRAM占用 | 6.20 GB（仅前向推理，训练时需更多） |

### PROMPT设置（tags.txt）
```
pop love song, male vocal, deep male voice, baritone, masculine vocal,
husky male voice, romantic, sweet, catchy melody, pop ballad, tender,
intimate, slow tempo, male singer, not female voice, low pitch male, 男声独唱
```

### ⚠️ 声线结果未知
截至2026-05-14 13:00，歌曲已生成并发送给用户，**尚未收到关于是否为男声的反馈**。如果RL版仍然是女声，则确认HeartMuLa开源版的声线性别控制完全不可靠。参考 `vocal-timbre-limitations.md`。

## 全部推理失败记录

### 错误1：ModuleNotFoundError: No module named 'heartlib'
原因：heartlib模块在 `src/heartlib/` 下。需要 `sys.path.insert(0, '/path/to/heartlib/src')`。

### 错误2：TypeError: from_pretrained() missing required positional argument: 'version'
原因：`from_pretrained(pretrained_path, version=..., ...)`，version是必填位置参数。

### 错误3：AttributeError: 'HeartMuLaGenPipeline' object has no attribute 'generate'
原因：API是 `pipe(inputs={...}, ...)` 不是 `pipe.generate(...)`。用 `__call__` 接收字典输入。

### 错误4：SafetensorError: incomplete metadata, file not fully covered
原因：model-00001-of-00004.safetensors 下载损坏。必须用 safe_open 验证，文件大小检查不够。

## 关键教训总结
1. 下载RL模型后必须用 `safetensors.safe_open` 验证所有分片——第一个文件最容易坏
2. 必须手动构建目录结构（子文件夹+symlink+复制tokenizer/gen_config）
3. `from_pretrained` 需要 `version="3B"` 参数
4. API用 `__call__` 传inputs字典，不是 `.generate()`
5. 用户反感看到后台进程输出——只报告自然结果
6. wget + `--tries=0` + `-c` 比 curl 更可靠下载大文件
