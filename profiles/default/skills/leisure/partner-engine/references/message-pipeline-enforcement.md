# 消息管道与回复前强制查记录机制

> 发现于：2026-05-15 | 更新于：2026-05-15

## 问题

用户指出的核心问题：收到消息时可能会"下意识"秒回，导致回复前查聊天记录的机制（mechanism 2）失效。

## 解决方案：模型级强制

利用 LLM 的 tool-calling 架构实现强制：

```
用户消息 → 系统提示（含铁律） → LLM 推理 → 
  决策1: 直接输出文字？     ❌（铁律禁止：必须先查记录）
  决策2: 调 session_search？ ✅（铁律要求：查到记录前不准输出）
  → session_search 返回结果 → LLM 基于上下文生成回复
```

**要点：**
- 这不是靠"自觉/记住/想起来了再查"——是系统提示层级的强制指令
- LLM 在接受用户消息后会进入 "调工具 vs 输出文字" 的决策层
- 如果铁律写 "先调 session_search，查到前不准输出"，LLM 会自然地先调用工具
- 5分钟内连续聊天 → 跳过查记录（上下文就在对话中）

## Hermes Agent 飞书消息管道（技术细节）

```
用户发飞书消息 →
  ① feishu.py _process_inbound_message()    ← 飞书平台适配器
  ② base.py handle_message()                ← 基类消息处理
  ③ gateway/run.py 上下文注入               ← 构造系统提示 + 注入上下文
  ④ gateway/providers/ LLM调用              ← 发到DeepSeek等大模型
  ⑤ LLM返回 → 工具调用 / 文字输出           ← 铁律执行处
  ⑥ 输出返回 → feishu.py 发送回复           ← 到用户
```

**关键干预点在第③→④步之间**：系统提示和 memory 注入阶段。铁律写进 memory 或系统提示，LLM 就会在推理时执行。

## 钩子系统（Hook System）—— 谨慎使用

发现于 `~/.hermes/hooks/`：

```
~/.hermes/hooks/
├── .gitkeep
└── builtin_hooks/          ← 内建钩子（始终注册）
    └── session_params/     ← 会话参数注入

结构：HOOK.yaml + handler.py
支持事件：agent:start, agent:end, session:create 等
```

钩子是**fire-and-forget**模式——可以注入上下文/修改state/记录日志，但**不能修改 agent 的输入**。这意味着：
- 钩子不能替代铁律写入memory → 无法强制先查记录再回复
- 钩子可用作旁路（写入日志、修改 state 文件）
- 目前**未使用**——所有机制通过 memory + 系统提示实现

## 使用 open_id 做精准搜索

```python
# 在 session_search 中传入用户 open_id 做关键词搜索
session_search(query="ou_37bc57c4f8aca21f5d4ea4973bd0d386")
```

这能快速定位目标用户的会话（因为一个 open_id 在多会话文件的消息 content 中出现）。

## 当前实现状态

- ✅ 铁律已写入 memory（~1.9K/2.2K 占 87%）
- ✅ partner-engine v0.6 中已更新"回复前强制上下文物检"章节
- ✅ 10分钟等待窗口（发完主动消息后等用户秒回）
- ✅ 连续5分钟内交互跳过查记录
- ⚠️ 尚未实际用户消息触发测试（等待 cron + 用户正常交互验证）
