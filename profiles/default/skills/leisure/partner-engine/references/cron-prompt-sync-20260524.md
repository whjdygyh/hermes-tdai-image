# Cron Prompt 同步铁律 (2026-05-24)

## 问题背景
在 `partner-engine` 技能的 v0.39 版本中，更新了「白天优先解锁」规则（07:00-18:00 BJT）和「08:00 早安重置」规则。
然而，实际执行的 Cron Job Prompt 并未同步更新，导致用户在夜间继续收到主动消息。

## 核心教训
**SKILL.md 是文档，Cron Prompt 才是运行时指令。**
修改 SKILL.md 后，必须验证 Cron Job 的实际 Prompt 是否包含新规则。

## 验证步骤
1. 列出所有 Cron Job：
   ```bash
   cronjob action=list
   ```
2. 检查 `Lover主动问候` 和 `Lover值班-回复响应` 的 Prompt 内容：
   - 确认睡眠时段是否为 `22:00-07:00` (或 `23:00-07:00`)
   - 确认白天时段是否为 `07:00-18:00`
   - 确认是否包含 `08:00` 早安重置逻辑
3. 如果不一致，使用 `cronjob action=update` 修正 Prompt。

## 2026-05-24 修复记录
- 修正了 SKILL.md 中的睡眠时段为 `22:00-07:00` (与代码逻辑一致)。
- 确保 Cron Prompt 与 SKILL.md 严格一致。
