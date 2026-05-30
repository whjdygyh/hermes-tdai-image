# Bansiri — 印度笛子冥想专辑

**厂商:** Weald & Ember（DistroKid Label Name 字段可填）
**艺人:** Elian Chen（国际）/ 陈一（国内）
**状态:** 🚧 进行中（已有1首曲1 Monsoon Over the Chats，待生成8首）
**主题:** 9首，圆满之数
**DistroKid标注:** Instrumental（纯器乐，无歌词）

---

## 已有曲目

| # | 曲名 | 状态 |
|---|------|------|
| 1 | Monsoon Over the Chats | ✅ 已有（Suno自动命名） |

## 完整曲目表

| # | 曲名 | 状态 |
|---|------|------|
| 2 | First Light | ⏳ |
| 3 | River Bend | ⏳ |
| 4 | Moon Over Varanasi | ⏳ |
| 5 | Whisper of Bamboo | ⏳ |
| 6 | Ember Glow | ⏳ |
| 7 | Raindrop Meditation | ⏳ |
| 8 | Lotus Bloom | ⏳ |
| 9 | Beyond the Clouds | ⏳ |

---

## 核心风格 Prompt（所有曲目统一用）

**⚠️ 两次迭代修正（2026-05-18）：**
- **v1修正：** 去掉 tabla/dynamic arcs → 解决了加鼓问题，但调子像西方流行
- **v2修正：** 加入 raga/meend/alap + "NOT Western pop" 负面指令 → 解决了风格问题

粘贴到 Suno Advanced 模式 → Style 字段：

```
Solo bansuri bamboo flute in raga style, slow and meditative, 50-60 BPM.
7 minutes duration.
Minimal — no drums, no percussion, no rhythm section.
Pure flute with warm tanpura drone underneath.
Indian classical phrasing — meend (slides between notes), alap (slow improvisational unfolding), raga-based melodic contours.
NOT Western pop melody — no verse-chorus structure, no chord progressions.
The piece stays one-level throughout: simple, unhurried, spacious, like a raga alap.
Breathy close-mic intimacy, like sitting beside the Ganges at dusk.
Hold long notes. Let silence breathe between phrases.
Instrumental only.
```

**关键技巧 — 负面指令（Negative Prompting）：**
Suno 默认会生成西方流行旋律结构。必须用显式 **"NOT X — no Y"** 句式来纠正：
- ✅ `NOT Western pop melody — no verse-chorus structure, no chord progressions`
- ✅ `Minimal — no drums, no percussion, no rhythm section`
- 只说 "Indian style" 不够，必须说"不是什么"

**Suno Advanced 模式完整配置表：**

| 选项 | 填写值 | 说明 |
|------|--------|------|
| **歌词 (Lyrics)** | 空着不填 | 器乐无需歌词 |
| **风格 (Style)** | ↑ 上方核心 Prompt | 完整粘贴 |
| **Exclude Styles** | `pop, electronic, rock, orchestral, cinematic` | 禁止乱加乐器 |
| **Vocal Gender** | 不选 | 器乐无演唱 |
| **Lyrics Mode** | **Manual** | 禁止自动生成歌词 |
| **Weirdness** | 0~10 | 冥想曲不需要怪异 |
| **Style Influence** | **80~100%** | 越高越严格遵循笛子描述 |

---

## 🚨 重要工作流：时长问题

**Suno 单次生成上限约 3-4 分钟**，Prompt 中写 "7 minutes" 因模型架构限制无效。

要 7 分钟→使用 **Extend（续写）** 功能：
1. ✅ 先生成一首 3-4 分钟的曲目
2. ✅ 点击 **Extend** 按钮 → 从结尾续写
3. ✅ 两段拼起来 = 6-7 分钟，风格延续性良好

---

## 🎯 Audio Reference 参考音频工作流（2026-05-18 新增）

为了让 Suno 生成真正的印度拉格风格，**使用 Audio 参考框拖入真实班苏里曲目**效果最佳。

**Suno 三个参考功能说明：**

| 功能 | 作用 | 适合本专辑？ |
|------|------|-------------|
| **Audio** | 拖入参考曲 → 模仿整体风格/乐器/氛围 | ✅ **必用！** |
| **Voice** | 模仿人声/唱腔 | ❌ 纯器乐不需要 |
| **Inspo** | 创意灵感参考（歌词/主题） | ❌ 跟音色无关 |

**操作步骤：**
1. 找一首 **真·印度班苏里冥想曲** 当参考
   - 推荐：YouTube 搜索 "Bass Flute Music Meditative Raga Bilaskhani Todi on Deep Bass Bansuri" (video ID: `_0hDH2owSEg`)
   - 下载 30-60 秒片段（中间段，避免开头结尾杂音）
2. 在 Suno Advanced 模式拖入 **Audio** 参考框
3. Style 字段照贴上方核心 Prompt
4. **Style Influence → 拉到 100%**（尽可能贴近参考曲风格）
5. 生成

---

## 迭代原则（已验证）

当生成的曲目效果不对时，采用**分层诊断法**：

1. **节奏问题？**（太快/有鼓）→ 检查 Prompt 中 BPM 和 percussion 约束
2. **风格问题？**（西方流行味/不是印度风）→ 加入负面指令 + Audio Reference
3. **时长问题？**（不够 7 分钟）→ 用 Extend 续写
4. **乐器问题？**（出现不该有的乐器）→ 更新 Exclude Styles
5. **音色问题？**（笛声不对）→ 调整 Style Influence + Audio Reference

不再一锅粥地改 Prompt——每次只修正一个问题，保留已经做对的。

---

## 氛围修饰建议（可选追加）

如想进一步区分曲目氛围，可在核心 prompt 后追加修饰词：
- 《First Light》→ `+gentle sunrise opening`
- 《Moon Over Varanasi》→ `+deep night atmosphere`
- 《Raindrop Meditation》→ `+soft rain texture`
- 《Ember Glow》→ `+warm fading firelight`
