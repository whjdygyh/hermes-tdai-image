---
name: chat-history-search
description: 搜索过往飞书聊天记录 — 当用户问"还记得吗""之前说过""上次聊到"时，自动查阅历史会话文件找回对话内容
version: 1.0.0
author: Lover
license: MIT
metadata:
  hermes:
    tags: [chat-history, session-search, memory-recall, conversation-lookup]
    related_skills: []
---

# 聊天记录搜索技能

## Trigger Conditions（触发条件）

当用户表达以下意图时**必须加载此技能**：

- "还记得我们之前说过…吗"
- "上次聊到…"
- "以前你说过…"
- "我之前提过…"
- "我们之前讨论过…"
- "你忘了之前…"
- 任何涉及查找过往对话内容的问题
- 你想不起来某事需要查聊天记录时

### ⚡ 强制触发（非自愿查询）

**每次收到用户消息且不在连续对话中（5分钟内无交互），系统提示中的铁律会强制你调用 `session_search` 查最近聊天记录。** 这不是选择，是模型级强制。

这个场景下**不需要加载本技能**——直接在记忆铁律驱动下调用 `session_search` 即可。本技能只在**主动搜索**（查特定关键词/时间范围的内容）时加载。

**⚠️ 重要补充：session_search 的覆盖范围有限**
session_search 不会索引全部 session 文件。它可能返回空，也可能返回几天前的旧结果但**漏掉最近几小时内新创建的 session 文件**。
- **验证方法：** 无论 session_search 返回什么，都必须继续做 Phase 2 直接文件检查（见 partner-engine §3 子场景 A2）。
- **备用方案：** 当 session_search(query) 失败时，尝试 `session_search()` 无参数浏览（browse 模式），可能发现活跃的 feishu 会话。

## 会话文件存储结构

```
存储目录：/home/admin1/.hermes/sessions/
文件名：  session_YYYYMMDD_HHMMSS_<hash>.json
总会话：  ~733个（截至2026-05）
总量：    ~120MB
```

### 每条会话JSON结构

```json
{
  "session_id": "20260510_000227_436dec",
  "model": "deepseek-v4-flash",
  "platform": "feishu",
  "session_start": "2026-05-10T00:02:27",
  "last_updated": "2026-05-10T00:07:03",
  "message_count": 77,
  "messages": [
    {"role": "user", "content": "用户消息..."},
    {"role": "assistant", "content": "我的回复..."},
    {"role": "tool", "content": "工具输出..."}
  ]
}
```

- `role: "user"` = 安迪说的话
- `role: "assistant"` = 我说的（Lover的回复）
- `role: "tool"` = 后台工具输出（可忽略，除非需要查技术细节）

## 搜索方法（按优先级）

### 方法零：查 cron job 执行状态 + state 文件（调试自动消息）

当用户问「你发消息了吗」「今天怎么没动静」时，先查 partner-engine 状态文件，再查 cron job 日志：

```bash
# 1. 查 cron job 列表和最近执行时间
cronjob action=list

# 2. 查 state 文件（last_outgoing 显示最后一条消息）
BASE=/home/admin1/.hermes/profiles/lover/home/.hermes/profiles/lover
cat "$BASE/state/last_outgoing.json"

# 3. 查 active_context 看用户最近互动时间
cat "$BASE/state/active_context.json"

# 4. 查 emotional_state 看心情历史
cat "$BASE/state/emotional_state.json"
```

**调试线索：** 如果 `last_outgoing.waiting_for_reply=true` 且时间戳是几个小时前，说明消息发了但用户没回→ partner-engine 的沉默锁生效了。  
**对比 cron job 的 `last_run_at`** — 如果 job 按时跑了但没发消息，说明决策树判定应静默，不是系统故障。

### 方法一：session_search 工具（首选，零成本）

使用内置的 `session_search` 工具：

- **无参数调用** → 返回最近会话概览（标题+预览+时间戳）
- **带关键词查询** → 搜索所有过往会话的摘要

```python
# 用法模式
session_search()                    # 浏览最近会话
session_search(query="关键词")       # 搜索特定话题
```

**最佳实践：** 关键词用 OR 连接（如 "血糖 OR 体检 OR 健康"）—— 默认 AND 容易漏结果。

### 方法二：grep 直接搜索 JSON 文件（深入搜索）

当 session_search 结果不够详细时，直接搜索用户消息内容：

```bash
# 搜索安迪（user）说过的内容
grep -rl '"role": "user"' /home/admin1/.hermes/sessions/ | head -5

# 搜索特定关键词（只搜用户消息，不搜工具输出）
grep -h 'content.*关键词' /home/admin1/.hermes/sessions/session_*.json | head -20

# 限定日期范围
grep -l '2026-05-0[1-5]' /home/admin1/.hermes/sessions/session_202605*.json | head -10

# 按内容精准匹配
python3 -c "
import json, glob, sys
keyword = sys.argv[1]
for f in sorted(glob.glob('/home/admin1/.hermes/sessions/session_*.json')):
    with open(f) as fh:
        data = json.load(fh)
    for m in data.get('messages', []):
        if m.get('role') == 'user' and keyword in str(m.get('content', '')):
            print(f['\${f.split(\"/\")[-1]}'] + ': ' + m['content'][:200])
            break
" "关键词"
```

### 方法三：Python 脚本深入分析

对于复杂搜索（时间范围+关键词+角色过滤组合），使用 execute_code 跑 Python：

```python
from hermes_tools import search_files, read_file, terminal
import json, glob
from datetime import datetime, timedelta

# 例如：搜索最近7天提到"血糖"的对话
result = terminal("""
python3 -c '
import json, glob, sys
from datetime import datetime, timedelta
cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
keyword = sys.argv[1]
matches = []
for f in sorted(glob.glob("/home/admin1/.hermes/sessions/session_*.json")):
    fname = f.split("/")[-1]
    file_date = fname.split("_")[1]
    if file_date < cutoff:
        continue
    with open(f) as fh:
        data = json.load(fh)
    for m in data.get("messages", []):
        if m.get("role") == "user" and keyword in str(m.get("content", "")):
            matches.append(f"{fname[:20]} | {m[\"content\"][:150]}")
            break
for m in matches[:10]:
    print(m)
' "血糖"
""")
```

## 搜索技巧

### 按日期段搜索

| 时间范围 | 文件前缀 | 示例 |
|---------|---------|------|
| 最近1天 | 今天的日期 | session_20260515_* |
| 最近7天 | 2026051[0-5]_* | grep session_2026051* |
| 特定日期 | 精确前缀 | session_20260510_* |
| 当月所有 | 年月前缀 | session_202605* |

### 按内容类型搜索

| 想找什么 | 搜索方法 |
|---------|---------|
| 安迪的某句话 | role=user + 关键词 |
| 我的回复 | role=assistant + 关键词 |
| 某个具体指令（如"记事"） | role=user + "记事" |
| 技术讨论（如"生图"） | role=user + "生图\|生成图片" |
| 亲密对话 | role=assistant + "亲\|抱\|想\|爱" |
| 健康数据 | role=user + "血糖\|糖化\|胰岛素" |

## ⚠️ 已知坑点

1. **当前会话不在文件中** — 正在进行中的对话还没写入 session JSON。只有**结束后**才会保存
2. **session_search 有3条限制** — limit 参数最多返回5条，搜不到时用 grep 补
3. **工具消息占大量空间** — role=tool 的消息可能占70%以上。搜索时最好只查 role=user 或 role=assistant
4. **文件大小** — 有些会话文件可能非常大（包含完整系统提示词、工具定义等），grep 整个目录可能稍慢
5. **会话文件名不是中文友好** — 按日期找最准确，不要试图从文件名猜内容
6. **⚠️ cron 输出文件才是消息全文的黄金来源** — 当搜索目标是「我自己发了什么」时，session JSON 中的 assistant 消息经常经过压缩/重写，**可能丢失了问句和具体措辞**。应当优先读 cron 输出文件：
   `~/.hermes/profiles/lover/cron/output/<job_id>/<timestamp>.md`
   定位"## Response"之后的文本块。session 文件只适合查「用户说什么/对话走向」。
7. **呈现搜索结果的常见陷阱** — 当用户问"我发了什么"时，不要只列日期和摘要标签。应该提取**消息全文中的问句、语气、钩子**一并呈现。一个消息的"钩子"（问句/调情/互动邀请）比"主题分类"重要得多——用户回复的就是那个钩子。
⚠️ **session_search 用 open_id 查询返回旧 cron 会话摘要** — 当用 `session_search(query="ou_37bc57c4f8aca21f5d4ea4973bd0d386")` 检测用户最近是否有新消息时，session_search 可能返回几天前的旧 cron session（这些 session 的摘要中提到了该 open_id），**看似"命中"但实际不是用户的新消息**。这是 cron session 的 session_id 和 summary 中会自然包含 open_id 导致的。**必须检查返回结果的 `when` 或 `session_start` 日期字段是否在目标时间之后**。仅返回旧结果 → 按"无新消息"处理，改用 grep 查真实 session 文件。

**补充：当 search(query) 失败时，尝试 browse()。** session_search() 无参数浏览会返回所有类型会话的概览（包括 feishu DM 会话），即使 search(query) 或 scroll(session_id) 无法访问这些会话。browse 结果中的 `last_active` 时间戳可用于检测用户最近是否活跃。详见 partner-engine `references/session-search-browse-fallback-20260524.md`。
9. **⚠️ 跨代理session混淆（v0.18新增）** — 系统级session目录 `/home/admin1/.hermes/sessions/` 包含所有Hermes代理的会话记录（Lover、国学术数、AI绘画等）。用grep/Python搜索时，关键字可能在任意代理的session中匹配到。**不要因为某个session里有用户的open_id就认定是与Lover的互动。** 验证方法：
   - 读前3条用户消息的内容判断归属（"老公/宝贝/想你" → Lover ✅；"电脑无线/八字/帮我算" → 其他代理 ❌）
   - 检查工具调用名称（feishu/send_message → Lover ✅；chinese-metaphysics → 其他代理 ❌）
   - 搜索时最好加上Lover专有词过滤，如"宝贝 OR 想你了 OR 老公"而非纯技术关键词
