# session_search Browse-vs-Search 缺口 — 2026-05-24 观察记录

## 场景

2026-05-24 19:33 BJT cron 傍晚维护唤醒。用户约 23 分钟前（19:10 BJT）在 feishu DM 会话中活跃过，会话标题 "调整消息发送时间 #11"。

## 核心发现

### 现象：Browse 可见 → 但 Query/Scroll 无法交互

session_search() **无参数浏览**返回了 3 个会话，包括 feishu 会话 `20260524_071047_900762`（最后活跃 19:10 BJT）。但：

| 操作 | 行为 | 结果 |
|------|------|------|
| `session_search(browse)` | 无参数浏览 | ✅ 返回 3 条（含 feishu 会话 + 2 cron 会话） |
| `session_search(query="ou_37bc57c4f8...")` | 按用户 ID 搜索 | ❌ 仅返回历史的 cron 会话（不含 feishu 会话） |
| `session_search(query="调整消息发送时间")` | 按标题关键词搜索 | ❌ 返回 cron 会话中的 skill 加载文本（不返回 feishu 会话自身） |
| `session_search(session_id, around_message_id)` | 滚动进入 feishu 会话 | ❌ "around_message_id not in session" 错误 |
| `session_search(query="feishu dm lover")` | 多关键词搜索 | ❌ "No matching sessions found" |

**结论：session_search browse 有独立的可访问路径，与 query/scroll 路径不同。feishu 会话在 browse 中可见，但 query/scroll 完全无法触及。**

### 根本原因（推测）

sessions.json 索引文件仅记录到 `session_id: 20260523_034540_d93652eb`（昨日会话）。今日 feishu 会话 `20260524_071047_900762` **不在 sessions.json 中**。session_search 的 browse 路径使用了不同的内部索引（可能直接从 session 目录文件系统读取），而 query/scroll 路径依赖 sessions.json 索引。

```
sessions.json 内容（截至19:33 BJT）:
  feishu DM key: agent:main:feishu:dm:oc_958418b03b0e7123379af3d1c1c26ded
  → 最新 session_id: 20260523_034540_d93652eb (昨天的会话)
  → 今日 20260524_071047_900762 未收录

session_search browse 结果:
  → 返回 20260524_071047_900762 (今日 feishu 会话)
  → 独立于 sessions.json 的索引
```

### 对 cron 流程的影响

**正效应（2026-05-24 实际验证）：** session_search browse() 返回了 feishu 会话的元数据（最后活跃时间 19:10 BJT），让我知道用户 23 分钟前还在聊天。这是正确的信号 → 决定 [SILENT]。

**负效应（潜在）：** 如果 cron 尝试用 query/scroll 深入访问该 feishu 会话获取更多上下文（具体用户说了什么、最后一条消息是什么），会反复失败，浪费多次 tool call。本会话中尝试了约 5 次 session_search 调用全部失败，最终靠 browse 结果中的 `last_active` 字段做决策。

## 实用启示

### 当 session_search browse 返回 feishu 会话时

```python
# browse 返回样本:
{
  "session_id": "20260524_071047_900762",
  "title": "调整消息发送时间 #11", 
  "last_active": "19:10 BJT",  # ← 这是关键字段
  "message_count": 30
}
```

✅ **正确用法：** 信任 browse 结果中的 `last_active` 时间戳。如果用户最近有活跃，这就是你需要的决策依据。不必深入读会话内容。

❌ **错误用法：** 尝试用 query 或 scroll 进入该会话获取详细信息（大概率失败）。

### cron 流程中的整合建议

在 Phase 1（session_search）阶段：

```
Step 1a — session_search(query=open_id, limit=3)
  → 返回旧结果或无结果 → 不信任，继续

Step 1b — session_search(browse without query)  
  → 核心检查浏览结果中的 feishu 会话
  → ✓ 如果返回的 feishu 会话 last_active 在最近 60 分钟内：
      用户刚刚或正在与你聊天 → 保持沉默，不发送任何 cron 消息
  → ✓ 直接信任 browse 结果中的时间戳（比 search 更可靠）
  → 注意：browse 返回的是标题+预览，不是完整消息内容
       足够做"是否活跃"的判断，但不足以做"用户说了什么"的判断
  
Step 1c — 如果 browse 中无活跃 feishu 会话
  → 进入 Phase 2（quick_session_scan 或直接文件检查）
```

### 2026-05-24 验证脚本

```bash
# 验证 sessions.json 中 feishu DM 最新 session_id
python3 -c "
import json
with open('/home/admin1/.hermes/sessions/sessions.json') as f:
    data = json.load(f)
# 搜索 feishu DM key
for key, val in data.items():
    if 'feishu' in str(key).lower() and 'dm' in str(key).lower():
        print(f'{key}: {val}')
"
# 输出: agent:main:feishu:dm:oc_958418b03b0e7123379af3d1c1c26ded: {'session_id': '20260523_034540_d93652eb', ...}
# → 索引中最新记录是 20260523（昨天），今日 feishu 会话未入索引
```

### 与现有坑点的关系

| 现有坑点 | 本观察的关系 |
|---------|-------------|
| `references/session-search-coverage-gap-20260516.md` — search 漏掉文件 | **互补：** 那个观察是 search(query) 返回空但文件存在；这个是 browse 显示存在但 query/scroll 不可交互 |
| common-errors 「session_search返回旧结果而非空」 | **相关：** open_id 搜索命中旧 cron 会话（false positive）。新问题：browse 可以正确找到 feishu 会话但 scroll 失败 |
| 常见错误表第一行「session_search返回空」 | **不同：** 这里不是"空"，而是"browse 有结果 + search 不一致" |
