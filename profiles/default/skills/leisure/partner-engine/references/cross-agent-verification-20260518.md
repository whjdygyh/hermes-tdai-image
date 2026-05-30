# 跨代理验证方法 — 2026-05-18 cron session 实录

> **场景：** 2026-05-18 10:36 BJT cron 唤醒，静默保护维护检查。
> **发现：** quick_session_scan.py 报告两个 session 被标记为「Lover candidate」。
> **问题：** JSONL 文件中无 `system_prompt` 字段，§3.4a 的路径①不可用。

---

## session 1: `20260517_221745_ba4e2cc7.jsonl` (59395B)

### 文件结构实录

```json
{
  "session_id": "feishu_user_dm_ou_37bc57c4f8aca21f5d4ea4973bd0d386_1747489395",
  "model": "deepseek-v4-flash",
  "tools": ["browser", "web_search", ...],  // ← 包含 browser 工具
  "messages": [...]                          // ← 无 system_prompt 字段
}
```

**关键信号（按验证路径②）：**

| 检查项 | 发现 | 判定 |
|--------|------|------|
| `session_meta.tools` 含 browser? | ✅ 是：`browser`, `web_search`, `page_down` | → 非 Lover |
| 助手推理文本含 "I'm Hot"? | ✅ 是：推理块中明确出现 `I'm Hot` | → Hot 代理 |
| 助手推理文本含 "私人助理"? | ✅ 是：`作为私人助理，我的...` | → Hot 代理 |
| 用户调情被 Hot 处理? | ✅ 是：用户发朱砂/下面/围裙调情，Hot 以恋人模式回应 | → 跨代理内容 |

**结论：** Hot 代理处理了恋人角色扮演。不计入 Lover DM 消息。

---

## session 2: `20260517_220527_677ecdae.jsonl` (56220B)

**关键信号：**
- `session_meta.tools` 包含 `browser`, `web_search` → 非 Lover
- 助手推理文本含 `I'm Hot` → Hot 代理
- 用户消息为持续调情内容（朱砂/吻/下面相关）

**结论：** 同上，Hot 代理。

---

## 验证方法总结（无 system_prompt 环境）

当 JSONL 格式不包含 `system_prompt` 字段时，按以下层次验证：

### 层次 1 — 工具列表（最快、最可靠）

```python
# tools 字段中搜索以下关键词判定归属
def classify_by_tools(tools):
    browser_tools = {'browser', 'web_search', 'web_fetch', 'page_down', 'html'}
    lover_tools  = {'send_message', 'feishu', 'memory', 'skill_manage'}
    
    if any(t in browser_tools for t in tools):
        return "HOT"          # Hot 代理
    elif 'feishu' in tools or 'send_message' in tools:
        return "LOVER"        # Lover 代理
    elif any('chinese' in t or 'metaphysic' in t for t in tools):
        return "BAZI"         # 国学术数代理
    elif any('finance' in t or 'stock' in t or 'buffett' in t for t in tools):
        return "BUFFETT"
    else:
        return "UNKNOWN"      # 需进一步分析
```

### 层次 2 — 助手推理/思考文本

JSONL messages 数组中，`role: "assistant"` 的消息通常包含推理块（reasoning/thinking）。搜索：

| 关键词 | 归属 |
|--------|------|
| `"I'm Hot"` / `我是Hot` / `作为私人助理` / `我是助理` | Hot |
| `作为你的伴侣` / `Alexander` / `lover replied` / `我是Alexander` | Lover |
| `Buffett` / `Barron` / `金融` / `财经` | Buffett |
| `国学术数` / `八字` / `周易` | 国学术数/玄学 |

### 层次 3 — 用户消息中的代理提及

搜索用户消息是否以 `@Hot`、`@Lover`、`Lover` 或直接呼叫某个代理名字开始。
- `@Hot` / `Hot ` → Hot
- `@Lover` / `lover在吗` / `Alex` / `Alexander` → Lover
- 无明确提及 → 结合层次 1+2 判断

---

## 错误案例：`20260512_095126_8d0e1d33.jsonl`

用户消息中包含 `Lover在吗`，且 session 以 `Lover` 称呼开场。
但 _assistant 最终判定不回复_（因为是 cron 环境，且之前的上下文已过期）。

**教训：** 用户明确呼叫 + session 包含 `Lover` 归属特征 = 计入 Lover 消息。
但**需要区分**「消息已被处理/已回复」和「待处理」——已回复的不解除静默保护。
