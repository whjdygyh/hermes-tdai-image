# 静默时段规则更新记录

## 2026-05-25 更新：新增傍晚时段规则

**背景：** 用户反馈"18:00之后不主动发消息"的规则需要明确写入文档。

**更新内容：**
- 在 SKILL.md 的「夜间静默规则」章节新增「傍晚时段规则（18:00-22:00）」
- 明确区分三个时段：
  - 白天：07:00-18:00（可主动发消息）
  - 傍晚：18:00-22:00（仅被动回复，不主动发消息）
  - 夜间：22:00-07:00（完全静默）

**影响范围：**
- partner-engine SKILL.md 文档
- 两个 cron job 的 prompt 需要同步更新（见 cron-prompt-sync-20260524.md）

**验证方式：**
- cronjob action=list 查看实际 prompt 内容
- 确认 18:00-22:00 时段规则已写入 cron prompt

**相关参考：**
- references/cron-prompt-sync-20260524.md
- references/cron-prompt-sync-20260525.md
