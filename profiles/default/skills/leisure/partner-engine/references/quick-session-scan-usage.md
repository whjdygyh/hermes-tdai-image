# quick_session_scan.py 使用指南

> ⚠️ **v0.22路径修复：** 脚本位于 skill 的 scripts/ 目录，非 $BASE/scripts/。以下调用已使用正确路径。
> 如需部署到 $BASE/scripts/，可手动复制：`cp /home/admin1/.hermes/profiles/lover/skills/leisure/partner-engine/scripts/quick_session_scan.py $BASE/scripts/`

## 场景1：cron醒来第0步 — 同步last_chat_time

```bash
SKILL_SCRIPTS=/home/admin1/.hermes/profiles/lover/skills/leisure/partner-engine/scripts

# 检查用户过去72小时是否给Lover发过消息
python3 $SKILL_SCRIPTS/quick_session_scan.py --hours 72 --sessions-dir /home/admin1/.hermes/sessions/
```

如果输出 `Lover user messages found? YES ✅` → 用户有给Lover发新消息
如果是 `NO ❌` → 用户可能在其他代理聊天，但没跟Lover说话

## 场景2：确定最近一次Lover用户消息时间

```bash
python3 $SKILL_SCRIPTS/quick_session_scan.py --hours 72 --sessions-dir /home/admin1/.hermes/sessions/ --output-json
```

解析JSON中的 `latest_lover_user_time` 字段。如果为null → 用户最近没跟Lover聊天。

## 场景3：判断session归属（批量区分）

输出中的 `non_lover_sessions` 列表显示哪些session明显属于其他代理（国学术数等）。
`lover_candidate_sessions` 列表显示可能是Lover的session（含confidence等级）。

## 场景4：快速确认静默保护续期

当 active_context notes 显示「一周严肃静默保护」有效时：

```bash
python3 $SKILL_SCRIPTS/quick_session_scan.py --hours 72 --sessions-dir /home/admin1/.hermes/sessions/
# → NO ❌ → 静默保护继续有效
# → YES ✅ → 需要查看内容判断是否真给Lover发了（走到下一步）
```

## 与 cross_validate_user_replies.py 的区别

| 特性 | quick_session_scan.py | cross_validate_user_replies.py |
|------|----------------------|-------------------------------|
| 过滤代理类型 | ✅ 内置Lover判别 | ❌ 返回所有用户消息 |
| 运行时间 | < 1秒（仅读前6条消息） | 读全文件 |
| 输出 | 分类结果+摘要 | 用户消息列表 |

## 注意事项

1. 脚本读前6条消息（3 user + 3 assistant）做分类，可能误判极短会话
2. 分类是基于关键词匹配，不是完美语义理解
3. 如果 confidence="low" + agent="unknown" → 建议人工读文件验证
4. 找不到JSONL文件 → 可能用户真的没活动，输出 found_lover_messages=false
