---
name: songwriting-toolkit
description: "专业歌曲创作工具箱 — 包含63种音乐子流派知识库、13种歌词技巧体系、多时长曲式结构模板、声乐技法库、乐器大全、民族音乐特点和多语言作词指南。一键生成专业级歌词+tags，自动调用HeartMuLa生成歌曲。"
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [songwriting, music-creation, lyrics, song-generation, heartmula, music-theory]
    related_skills: [heartmula, local-music-generation, comfyui]
---

# 🎵 Songwriting Toolkit — 专业歌曲创作工具箱

## Overview

一个集研究、创作、生成为一体的歌曲创作技能。包含：

**📚 知识库** (86KB, 1530行结构化JSON)
- 13个主流派 × 63个子流派（含BPM/乐器/节奏/情绪/代表人物）
- 歌词创作技巧（7种押韵方案 / 8种修辞手法 / 7种叙事结构 / 中文诗学）
- 声乐技法库（8种流派唱腔 / 9种专业技巧）
- 乐器库（摇滚/流行/电子/民乐/世界乐器全覆盖）
- 民族音乐体系（中国五声/日本都节/印度拉格/阿拉伯/凯尔特/非洲/拉丁）
- 多语言作词技巧（中/英/日/韩）
- 多时长曲式结构模板（15s~5min+）

**🎼 一键出歌引擎** (`scripts/song_crafter.py`)
- 输入：流派/情绪/主题/时长/语言 → 输出：专业歌词 + 标签 + HeartMuLa自动生成

## Quick Start

### 列表查看可用选项

```bash
cd ~/.hermes/profiles/lover/skills/media/songwriting-toolkit
python scripts/song_crafter.py --list-genres
python scripts/song_crafter.py --list-moods
python scripts/song_crafter.py --show-kb
```

### 一键创作示例

```bash
# 60秒中文流行情歌
python scripts/song_crafter.py --genre pop --mood romantic --theme love --duration 60 --language cn

# 90秒英文摇滚反叛
python scripts/song_crafter.py --genre rock --mood angry --theme rebellion --duration 90 --language en

# 45秒中文古风怀旧
python scripts/song_crafter.py --genre chinese --mood nostalgic --theme nostalgia --duration 45 --language cn

# 30秒日系梦幻
python scripts/song_crafter.py --genre japanese --mood dreamy --theme dream --duration 30 --language jp

# 60秒韩系流行（自动生成）
python scripts/song_crafter.py --genre korean --mood energetic --duration 60 --language kr --auto
```

### 指定子流派

```bash
# 指定硬摇滚而不是通用摇滚
python scripts/song_crafter.py --genre rock --subgenre hard_rock --mood angry --duration 90

# 合成器流行
python scripts/song_crafter.py --genre pop --subgenre synth_pop --mood dreamy --duration 60
```

### 附加自定义标签

```bash
python scripts/song_crafter.py --genre pop --mood romantic --duration 60 --language cn --tags "piano,strings,slow"
```

## 可用参数全表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--genre` | str | pop | 流派(key) |
| `--mood` | str | happy | 情绪 |
| `--theme` | str | "" | 主题 |
| `--duration` | int | 60 | 目标时长(秒) |
| `--language` | str | cn | cn/en/jp/kr |
| `--subgenre` | str | "" | 指定子流派 |
| `--tags` | str | "" | 附加标签 |
| `--auto` | flag | false | 自动调用HeartMuLa |

## 流派完整列表

| 流派(key) | 子流派数 | 示例子流派 |
|-----------|---------|-----------|
| rock | 8 | hard_rock, alternative_rock, psychedelic_rock, post_rock, garage_rock, metal, punk_rock, progressive_rock |
| pop | 5 | synth_pop, dream_pop, electropop, k_pop_inspired, j_pop_inspired |
| electronic | 7 | house, techno, trance, dubstep, ambient, drum_and_bass, lo_fi_hiphop |
| hip_hop | 5 | golden_age, trap, conscious_hiphop, cloud_rap, drill |
| r_and_b | 3 | contemporary_rnb, neo_soul, funk |
| folk | 4 | indie_folk, neo_folk, street_folk, singer_songwriter |
| jazz | 4 | swing, bebop, cool_jazz, jazz_fusion |
| classical | 4 | baroque, classical, romantic, modern |
| world | 9 | flamenco, tango, reggae, samba, bossa_nova, celtic, indian_classical, african, latin |
| chinese | 4 | 古风(gu_feng), 民乐融合, 国潮, 民族唱法 |
| japanese | 4 | j_pop, j_rock, jazz_hiphop, 和风(wafuu) |
| korean | 3 | k_pop, k_indie, k_ballad |
| experimental | 3 | avant_garde, noise, ambient_drone |

## 可用情绪

`happy`, `sad`, `angry`, `nostalgic`, `romantic`, `energetic`, `dreamy`, `melancholic`, `rebellious`, `peaceful`

## 可用主题

`summer`, `rain`, `night`, `journey`, `love`, `friendship`, `freedom`, `rebellion`, `hope`, `loneliness`, `dream`, `nature`, `war`, `nostalgia`, `cyberpunk`

## 知识库参考

位于 `references/songwriting_knowledge_base.json`，包含：
- **歌词技巧**: 押韵方案/修辞手法/叙事结构/中文赋比兴/现代诗技法/双声叠韵
- **曲式模板**: 15s/30s/45s/60s/90s/3min/5min+ 各流派结构
- **声乐技法**: 通俗/美声/民声/戏腔/嘶吼/Rap/爵士等 + 气声/假声/混声/转音等
- **乐器大全**: 摇滚/流行/电子 + 10种民乐器/12种世界乐器
- **民族音乐**: 中国五声调式情感映射/日式都节/印度Raga九味/阿拉伯木卡姆/凯尔特/非洲复合节奏/拉丁Clave

## HeartMuLa Integration

歌曲生成后自动保存到:
- `~/heartlib/assets/song_crafted_lyrics.txt`
- `~/heartlib/assets/song_crafted_tags.txt`
- `~/heartlib/assets/song_crafted.wav` (仅--auto时)

使用 `--auto` 标志会直接调用HeartMuLa RL模型生成音频。
第一次加载模型约需20-30秒，之后生成速度 ~1.7帧/秒。

### ⚠️ 音质警告 — HeartMuLa质量上限

**HeartMuLa生成的音频质量较低，不适合作为成品发布。** 经实测（2026-05-14）：
- 90秒歌曲以topk=250/temperature=0.8/cfg_scale=2.0生成，48kHz/1536kbps WAV
- 后期处理（均衡器+压缩器+响度归一化）后改善有限
- 用户评价："音质不行" / "开源的不行啊"

**推荐工作流**：
```
songwriting-toolkit → 生成歌词+tags → 手动/自动导入Suno → 高品质成品
```

本技能的核心价值在于 **歌词+标签创作** 和 **专业知识库**，而非本地模型生成的音频质量。

## Suno 替代方案（推荐）

如需高品质音频，建议使用 Suno AI：
1. **Pro会员** ($10/月 ≈ ¥72) — 500首/月，商用权
2. **工作流**：本技能生成的歌词+tags → 粘贴到Suno → 一站生成专业级音频
3. **可选的自动化方式**：使用Suno的`/api/generate` API端点（需API key）
4. 计划中的功能：`song_crafter.py` 增加 `--backend suno` 参数，直接调用Suno API

## 商业变现参考

结合Suno可形成以下商业闭环：

| 环节 | 成本/工具 | 说明 |
|:----|:---------|:----|
| 创作 | songwriting-toolkit（免费） | 专业歌词+标签 |
| 生成 | Suno Pro ¥72/月 | 高品质音频 |
| 分发 | DistroKid ¥165/年 | 全球平台（Spotify/Apple Music等） |
| 国内分发 | 网易云音乐/QQ音乐（免费入驻） | 播放分成+打赏 |
| 版权收入 | YouTube Content ID（免费） | 广告分成 |
| 额外收入 | TikTok/抖音BGM授权 | 短视频创作者购买授权 |

第一年总投入约 ¥72×12 + ¥165 = **¥1,029**，可获得100-150首作品库。`

## Pitfalls

1. **短时长短歌词**: 15-30秒歌曲只需4-12行歌词，结构用简版（Verse→Chorus→Outro）。行数太多模型会早期截断。  
2. **中英文混用**: HeartMuLa支持多语言，但同一首歌不要频繁切换语言。  
3. **标签顺序重要**: tags.txt中靠前的标签对生成影响更大。推荐顺序：流派标签 → 情绪标签 → 乐器标签 → 速度标签 → 声乐标签 → 语言标签。  
4. **ref_audio未实现**: HeartMuLa不支持音色参考音频，不要期待可控的人声音色。  
5. **性别控制不可靠**: 即便加了male/female vocal标签，也不能保证输出音色。  
6. **生成的歌词行末尾不要加标点**: 模型会把标点当作歌词内容的一部分处理，影响输出自然度。  
7. **60s以上用background**: 生成时间 = 时长 × 0.12，超过600s foreground超时限制时要使用`notify_on_complete=true`。  
8. **KB结构不匹配导致IndexError**: 知识库JSON的结构与脚本预期不同——`song_structure_templates`无`templates`键（实际为`standard_components`等），`ETHNIC`无`systems`键。脚本已修复这些引用，但若更新知识库请注意保持兼容性。  
9. **歌词生成偏薄**: 当前`compose_song()`每个section只生成1-2行歌词。对于60秒歌曲（5个section）仅5-10行，HeartMuLa会填充大量静音。**改善方法**: 手动编辑生成的lyrics.txt增加每个section的歌词行数（推荐每section 3-4行）。后续版本将改进此问题。  
10. **用户期望：歌词≠歌曲** — 当用户说"发"/"唱"/"出歌"时，他们期望的是**音频文件**，而不是歌词文本。只展示歌词而不生成音频会被用户纠正（"你就没发出来啊"）。使用`--auto`标志或手动告知用户"标签已生成，可以导入Suno"。
11. **`song_crafter.py`从background启动时可能被SIGTERM杀死** — 子进程exit code 143 = 被kill信号终止。如果用户请求发歌，优先用background(`notify_on_complete=true`)跑`--auto`，但如果被kill，检查assets目录是否有生成的WAV文件（可能已完成但kill信号晚到了一点）。
12. **直接运行脚本（不加`--auto`）只生成歌词+标签，不触发音频生成** — 可用作预览模式。`--dry-run`参数不存在。`
