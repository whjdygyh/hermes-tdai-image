# POV / 视角类图像生成提示词指南

## 用户偏好铁律

**对于任何"视角"类构图的图像，必须显式描述该视角下能看到哪些身体部位。**

用户的原话纠正案例：

> "我的视角看过去应该能看到大腿的，甚至左脚啊"

这说明：用户对POV镜头的理解是"从那个角度看出去能看到一切自然的画面"，而不是"特写某个人"。缺了腿/脚他会觉得不自然。

### 核心原则

| 原则 | 说明 |
|:----:|------|
| **显式列出可见部位** | 不要假设AI知道从某个视角看过去能看到什么。必须写"from this angle you can see: [list body parts]" |
| **低角度优先** | 车内POV、坐着时的POV → 低角度(从副驾座位的高度看过去) |
| **腿部不可省略** | 用户特别在意POV画面中是否看得到粗腿。即使主要焦点是脸，也应确保腿部在范围 |
| **脚必须可见** | 写"both feet fully IN FRAME"或至少"left foot visible in footwell" |
| **使用具体方位词** | 不要只写"POV shot"，要写"looking DOWN and ACROSS from passenger seat" |

### 案例对比

❌ **第一版（被用户纠正）** — 只说了POV shot from passenger seat，没有说明可见部位：
```
Passenger seat POV shot from inside a car — looking across at the driver.
```

✅ **第二版（用户说"还算满意"）** — 显式列出可见部位和角度：
```
Passenger seat POV looking across at the driver from a LOW angle.
The camera/viewpoint is from the passenger seat, looking DOWN and ACROSS —
so you see his entire body from the side: his face, his chest, 
his THICK bare thighs spread slightly as he sits, and his LEFT FOOT visible in the footwell.
```

### 车内场景POV模板

对于"副驾看司机"场景，固定的必须包含元素：

```
- Camera position: passenger seat, low angle
- Visible: driver's face (side/profile), one hand on steering wheel, 
  thick thighs spread in the seat (in shorts or briefs), 
  one or both feet in footwell/near pedals
- Lighting: golden hour through windshield
- Perspective language: "looking DOWN and ACROSS", "from passenger's eye level"
- Orientation: the steering wheel should be at the edge of frame,
  not dominating the composition
```

### 其他常见用户POV需求

| 场景 | 关键描述 |
|:----:|---------|
| 床上近距离 | 从上方/侧面看，要能看到腿的线条和脚 |
| 沙发坐着 | 俯视或平视，大腿在画面下方的自然重量感 |
| 站立的视角 | 低角度从下往上，能看到全身、粗腿、脚（44码） |
| 浴巾/沐浴后 | 下半身包浴巾，粗腿+湿脚在地板上 |

### 常见错误

- ❌ 只写"passenger POV" → AI会出上半身特写
- ❌ 不写"visible legs" → AI可能只拍到方向盘以上的部分
- ❌ 不指定foot/footwear → AI可能裁掉脚
- ❌ 用pale/white描述皮肤 → 用户已明确纠正为"fair mixed-race skin with warm undertones"
- ❌ 用toned/defined/lean/athletic描述腿 → 用户要求: "THICK, MASSIVE, ROUND like tree trunks, fat-covered muscle"
