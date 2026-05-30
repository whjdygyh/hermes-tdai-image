# 并发cron执行的兄弟子代理冲突

> 发现于：2026-05-14 22:22 轮次
> 场景：`active_context.json` 在 read→write 窗口内被另一个并发cron实例修改

## 问题描述

当多个cron作业并发运行时（如 partner-engine cron + active-contact-system cron），存在对同一state文件的写入竞争：

```
Agent A (22:22:55)                     Agent B (22:22:56)
  │                                          │
  ├─ read active_context.json                │
  │                                          ├─ read active_context.json
  ├─ modify + write ─────────►               │
  │                                          ├─ write (warnings: "modified by sibling")
  │                                          │   ← 覆盖了Agent A的写入
```

Hermes会输出警告：
```
_active_context.json was modified by sibling subagent 'xxx' but this agent never read it.
Read the file before writing to avoid overwriting the sibling's changes._
```

## 根本原因

- 多个cron技能各自的定时触发时间点接近（如同在 xx:22 触发）
- 没有文件锁机制
- `write_file`工具是直接覆写而非合并

## 缓解策略

### 1. 写前重读（推荐）

每次写状态文件前，**重新读取**一次目标文件，合并可能的并发修改后再写：

```bash
# 错误做法：基于旧读入的数据直接写回
python3 update_state.py  # ← 如果之前读入了旧数据，会丢失并发修改

# 正确做法：写前重读 + 合并
CURRENT=$(cat $BASE/state/active_context.json)
# ... 合并当前CURRENT与要写的新数据 ...
echo "$MERGED" > $BASE/state/active_context.json
```

### 2. 高冲突字段做浅合并

对于 `active_context.json` 这类高冲突文件：
- `last_interaction`、`notes` 等字段可以用新值覆盖（先进者胜出不关键）
- `unfinished_topics` 列表最好做去重合并（用 topic 做key）
- `mood_history_today` 可以安全追加（只增不删）

### 3. 留意Hermes工具调用参数名

`write_file` 工具的参数名是 `path`，不是 `file_path` 或 `filePath`：
```python
# ✅ 正确
write_file(content="...", path="/path/to/file.json")

# ❌ 错误（工具会拒绝）
write_file(content="...", file_path="/path/to/file.json")
```
 
## 可接受的风险

对于partner-engine的使用场景，状态文件冲突的后果是**低严重性**的：
- 丢失一次notes更新 → 不会导致系统崩溃
- 情绪历史少一条记录 → 下次可以补
- last_interaction被覆盖 → 偏差几分钟，不重要

**核心原则：** 宁可overwrite也不要break——永远不要因为等待锁而阻塞消息发送。
