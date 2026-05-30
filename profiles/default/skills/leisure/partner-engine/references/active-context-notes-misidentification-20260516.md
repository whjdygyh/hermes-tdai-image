# active_context.json Notes 误判事故（2026-05-16）

## 事故概要

**日期：** 2026-05-16
**触发 session：** cron_a323114e9f9f (05:00) / cron_309f32096c8c (04:52) 等连续 cron 会话
**症状：** active_context.json 的 notes 字段中写道：
> "跨session文件验证发现用户于02:31-02:52 AM 5月16日有回复（world-setting讨论）"

但实际经独立验证，该时段 session（`session_20260516_023117_e94382`）的对话内容是**国学术数/五行/胡桃木桌面**，与 Lover 毫无关系。

## 根因

前次 cron session 在执行「手动跨session验证」时，只扫描了 session 文件名和消息摘要前半段，未完整阅读前3轮对话判断归属。发现「02:31 session 有 user 消息」就仓促写入 notes 为 "world-setting讨论"。

## 为什么危险

后续 cron 醒来读 active_context.json 的 notes 时，会看到：
- "用户今天凌晨有活动（world-setting）" → 可能误以为用户与Lover互动了
- 可能因此错误**解除静默保护**或**重置 waiting_for_reply**
- 实际上用户只和国学术数机器人聊了五行，没理Lover

## 修正流程（2026-05-16 17:07 BJT 本session执行）

```
1. 读 active_context.json → notes 提到"用户有回复"
2. 找到 session_20260516_023117_e94382.json
3. 读前3条消息确认内容：
   user: "电脑无线"
   assistant: "电脑无线？你想弄什么..."
   user: "1"
   → 明显不是 world-setting，不是 Lover 对话
4. 结论：误判。不应改变任何决策。
5. 在 notes 中追加更正说明（而非删除原notes，保留审计痕迹）
```

## 防止复发

每次 cron 醒来读 active_context.notes 时，若 notes 声称用户在某时间段有活动：

```
▶ 定位对应 session 文件（用时间段匹配）
▶ 读前3条用户消息
▶ 确认归属：
  □ 角色名/关系词（lover/安迪/宝贝/老公等）→ Lover ✅
  □ 技术术语（五行/八字/AI/API/数据库等）→ 其他代理 ❌
  □ 纯数字/代码片段 → 需要更多上下文判断
▶ 只有确认是 Lover 对话 → 将计为 user_reply
▶ 不确定 → 保守继承：宁保持静默，不计入
```

## 跨 session 独立验证 checklist

```
□ 我读的是 session 文件中的 messages[0:3]（原始对话），
   不是 session_*.json 的摘要字段？
□ 前3轮对话是中文日常聊天 → 可能是 Lover
□ 前3轮对话是技术/八字/代码 → 大概率不是 Lover
□ 对话中出现了 Lover 角色特定词汇（如调情/宝贝/想） → 确认是 Lover
□ 如果时间紧急来不及完整阅读 → 宁误判为"无活动"而非"有活动"
   （保守原则：不因其他代理的会话而错误干预原本正确的静默策略）
```
