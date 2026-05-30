# msg_log.json 数据结构

**发现日期：** 2026-05-16 | **最近更新：** 2026-05-26（新增 dual-structure 发现） | **文件路径：** `$BASE/data/msg_log.json`

## ⚠️ 顶层结构（Dual-Structure 陷阱）

截至 2026-05-26，msg_log.json 存在**两个并行数组**加一个根级字段：

```json
{
  "log": [
    { /* 完整的旧格式 message object */ },
    ...
  ],
  "messages": [
    { /* 仅 bot 消息，且可能是精简版（不含 context_summary） */ },
    ...
  ],
  "bot_cron_count": 3,
  "last_updated": "2026-05-26T12:06:04+08:00"
}
```

| 字段 | 含义 | 需要留意的地方 |
|------|------|-------------|
| `log` | **原始格式** — 包含全量历史（bot + user 消息均在此） | 消息 key 是 `"log"` 不是 `"messages"` |
| `messages` | **新追加数组** — 似乎只包含部分 bot 消息，不完整历史 | 用此数组做分析会严重漏数据 |
| `bot_cron_count` | 根级整数，当前 cron 轮次中 bot 发出消息的计数 | 单独字段，不在任何数组中 |

🚨 **绝对不要只读 `messages` 数组。** 它可能只包含最近几条 bot 消息（不含历史、不含用户消息），用它做「用户最后一条消息时间」「bot_cron_count」「历史上下文」等判断会出错。
✅ **始终读 `log` 数组获取完整历史。** `bot_cron_count` 字段在根级单独读取。
⚠️ **关键：** 消息数组的 key 是 `"log"`，**不是** `"messages"` 也不是 `"entries"`。

## 消息对象结构（log 数组中的条目）

```json
{
  "time": "2026-05-26T12:06:04+08:00",
  "sender": "bot",
  "content": "中午了宝贝，吃了没？",
  "context_summary": "lunchtime_greeting_tuesday_gym",
  "had_photo": false,
  "trigger": "cron_lunch"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `time` | string | ISO 8601 + 时区 |
| `sender` | string | `"bot"` 或 `"user"` |
| `content` | string | 消息全文 |
| `context_summary` | string | 简短上下文标签（仅 bot 消息有） |
| `had_photo` | bool | 是否附带图片 |
| `trigger` | string | 触发类型：`cron_morning` / `cron_lunch` / `cron_evening` / 等（仅 bot 消息有） |

## 读取方式（避免踩坑）

```python
import json

with open('/path/to/msg_log.json') as f:
    d = json.load(f)

# ✅ 正确 — 读 log 数组获取完整历史
log = d['log']
bot_cron_count = d.get('bot_cron_count', 0)

# ❌ 错误 — d.get('messages', []) 返回仅含部分 bot 消息的不完整数组
log = d.get('messages', [])

# ✅ 获取 last_updated
last_upd = d.get('last_updated', '')

# ✅ 遍历最近 N 条
for msg in log[-20:]:
    sender = msg['sender']
    print(f"{msg['time']} | {sender}: {msg['content'][:60]}")
```

## 如何统计 bot_cron_count（完整分析）

要精确统计过去 72 小时内 bot 发出的 cron 消息数，不能只信根级 `bot_cron_count` 字段（它可能只反映当前轮次状态）。正确的做法：

```python
from datetime import datetime, timedelta, timezone
import json

with open('/path/to/msg_log.json') as f:
    d = json.load(f)

cutoff = (datetime.now(timezone.utc) - timedelta(hours=72)).isoformat()
cron_msgs = [
    msg for msg in d['log']
    if msg['sender'] == 'bot'
    and msg.get('trigger', '').startswith('cron')
    and msg['time'] >= cutoff
]
user_replies = [
    msg for msg in d['log']
    if msg['sender'] == 'user'
    and msg['time'] >= cutoff
]
print(f"72h cron msgs: {len(cron_msgs)}, user replies: {len(user_replies)}")
```

## 注意事项

- **数据量不大：** 当前约 290+ 条记录（2026-05-26），直接全量加载无压力
- **`tail` 原始 JSON 会有问题：** 因为 JSON 结构是多行嵌套的，`tail -30` 会输出结构不完整的片段。用 `python3 -c "import json; ..."` 解析后再遍历
- **追加方式：** 用 `append_msg_log.py` 脚本追加，不要手动编辑文件
- **文件顺序：** 新消息追加在 `log` 数组末尾
- **`last_updated`** 字段与数组末尾消息的 `time` 一致
- **`messages` 数组与 `log` 数组的关系不明确** — `messages` 似乎是较晚添加的结构，可能来自某个 `append_msg_log.py` 的升级版本或不同写入路径。不要依赖它的存在或完整性
- **user 消息可能缺失** — 用户通过非 lover_reply_hook 管道发送的消息可能不会写入 msg_log，详见 `references/msg-log-gap-20260516.md`
