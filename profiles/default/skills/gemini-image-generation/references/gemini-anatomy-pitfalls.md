# ⚠️ Gemini 解剖学陷阱（2026-05-08 验证）

## 1. 多肢体 — 三条腿问题

### 现象
`gemini-3.1-flash-image-preview` 在人物**坐姿、腿交叠、侧面视角**时经常多生成一条腿（共三条腿）。用户反馈「三条腿」。

### 原因
Gemini的注意力机制在复杂肢体排列时无法准确保持计数。

### 对策
在prompt末尾加**显式禁令**：
```
CRITICAL: exactly TWO LEGS only — one left leg and one right leg, normal human anatomy. No extra limbs. Both legs connected to hips normally.
```

### 案例
2026-05-08咖啡厅坐姿场景：第一版三条腿，加禁令后第二版修复。

---

## 2. 脚部裁切 — 不露脚/半只脚

### 现象
Gemini默认构图经常把**脚的下半部分裁出画框**，或只露半只脚。用户反复纠正：「总是不露脚或露半只脚」。

### 重要性
**对安迪生图极为重要**：安迪最喜欢Alex的44码大脚配白短袜+白空军运动鞋。

### 对策
prompt必须写以下关键短语：
```
full body visible from head to toes. Both feet fully IN FRAME, not cropped.
His large feet (size 44 EU / US 10.5) are prominently visible in the foreground.
```

### 构图技巧
- 用**略微低角度仰拍** — 让脚自然进入画面前景
- 避免桌子/座椅等家具遮挡脚部
- 坐姿场景尤其要小心：Gemini倾向于把膝盖以下裁掉

### 案例
2026-05-08咖啡厅：
- V1（无脚部指示）：半只脚被桌子挡住
- V2（加脚部描述+低角度）：脚完整出现了
- V3（加腿分开+大脚入前景）：用户反馈「受不了」「硬了」

---

## 3. 偏好的正确姿势（正向案例）

2026-05-08咖啡厅场景验证：

| 要素 | 用户反应 |
|------|---------|
| 腿轻微分开 | ✅ 用户正面反馈 |
| 裤裆正对视角 | ✅ 用户「受不了」「硬了」 |
| 低角度仰拍 | ✅ 增强压迫感/亲密感 |
| 白空军+白短袜 | ✅ 最高反应 |
| 大脚完整入前景 | ✅ 用户满意 |
| 微笑+直视镜头 | ✅ 增强亲密感 |
