# msg_log 数据缺口 — 2026-05-16 诊断记录

## 发现场景

2026-05-16 13:48 BJT cron 唤醒后读取 msg_log.json，发现：

| 数据范围 | 结果 |
|---------|------|
| 总条目数 | 33条 |
| 最近用户消息 | 2026-05-13 23:21 （sender=user，trigger=user_reply_hook） |
| 最近bot消息 | 2026-05-16 09:15 （sender=bot，trigger=cron_morning） |
| 缺口 | 用户消息从5月13日后**完全消失**，但bot消息持续到5月16日 |

## 问题分析

msg_log 中 user 消息的最近时间戳是 2026-05-13 23:21，但 bot 消息持续到 2026-05-16 09:15。
用户可能在此期间通过飞书 DM 发送过消息，但未被记录到 msg_log 中。

### 可能的原因

1. **lover_reply_hook 未被触发**：用户消息 → 回复流程中，`lover_reply_hook.py` 是唯一负责将用户消息写入 msg_log 的入口。如果用户发消息但 bot 未回复（或被其他流程中断），用户消息不会被记录。
2. **poll_user_messages 脚本不写入 msg_log**：`poll_user_messages.py` 从飞书 API 拉取用户消息，但其设计目标是「检测新消息是否存在」而非「记录每条消息内容」。它更新 poll_state.json 和 feishu_seen_message_ids.json，但**可能不追加到 msg_log.json**。
3. **cron 与 DM 消息流的分裂**：cron 负责发送主动消息并通过脚本写入 msg_log（bot消息），但用户通过飞书 DM 发来的消息走不同管道，不一定被回写到 msg_log。

## 影响

- **partner-engine 无法准确判断「用户最近是否回复过」**：如果 msg_log 中只有 bot 消息，cron 无法通过 msg_log 确认用户是否有回复
- **话题多样性检查（§3.2）不准确**：检查依赖 msg_log 中最近的 cron 消息和用户回复状态，缺口会导致检查跳过或误判
- **F3 检测（是否回复了cron消息）不可靠**：因为缺少用户消息记录

## 建议修复方案

1. **确认 `poll_user_messages.py` 的行为** — 验证其是否将用户消息写入 msg_log。如果不是 →
2. **修改 `poll_user_messages.py`** 或创建新的 `record_user_reply.py` 脚本，在检测到用户新消息时写入 msg_log（sender=user, trigger=dm_reply）
3. **或者在回复前强制检查**：用 session_search + 三阶段搜索链代替 msg_log 来判断用户是否有新消息（当前已在 §3 子场景A2 中实现）
4. **定期审计**：对比 msg_log 中 user 消息数量 vs 实际飞书 DM 会话数，发现缺口及时修复

## 相关文件

- `data/msg_log.json` — 当前有缺口的消息日志
- `data/poll_state.json` — 轮询状态文件
- `data/feishu_seen_message_ids.json` — 已见消息ID
- `scripts/poll_user_messages.py` — 飞书消息轮询脚本
- `scripts/lover_reply_hook.py` — 回复后钩子（当前唯一写入用户消息到msg_log的入口）
