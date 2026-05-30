# 静默保护维护验证 2026-05-19 15:55 BJT

## 概览

3天静默保护（5/18 16:08恢复）的第1天维护。端到端验证 §3.4a 流程 + **全量 .json 格式扫描**（本方 Hermes 环境以 `.json` 为主导格式）。

## 执行流程

| 步骤 | 动作 | 结果 |
|------|------|------|
| ⏰ | curl 百度 HTTP 头获取 GMT → +8h → BJT | ✅ 15:55 BJT |
| 📂 | 读所有 state 文件 (4 个) | ✅ 正常；静默保护标记正确 |
| 🔍 | quick_session_scan.py (v0.32+, 2日回溯) | ✅ 130 session 扫描；Lover 用户消息未发现 |
| 🧪 | 补充 .json 格式全量扫描 (37 个文件) | ✅ 全部 Hot 代理 |
| 🧪 | 确认今日无新 session | ✅ 20260519 文件名零匹配 |
| ✅ | 最终决策 | ✅ [SILENT] 保持保护 |

## 关键技术细节

### 双格式扫描策略（本 session 确认可靠）

```
Phase A — JSONL 快速扫描（primary）
  quick_session_scan.py --since "2026-05-17T16:00:00+08:00" --sessions-dir /home/admin1/.hermes/sessions/
  → 自动分类 Lover / 非 Lover
  → 全覆盖 session_meta.tools 分析

Phase B — JSON 补充扫描（secondary，覆盖盲区）
  execute_code(code="...") 直接运行 Python，使用 system_prompt 开头 200 字符做 agent header 匹配
  → 检查 '# Lover' / '你的名字：Lover' in sp[:200]
  → 检查 '# Hot' / '你的名字：Hot' in sp[:200]
  → 其他 → 未知代理
```

### system_prompt header 检查（最可靠的方法）

```python
# ✅ 正确的 agent 归属判断
sp = d.get('system_prompt', '')
is_lover = '# Lover' in sp[:200] or '你的名字：Lover' in sp[:200]
is_hot   = '# Hot' in sp[:200] or '你的名字：Hot' in sp[:200]

# ❌ 错误的做法（会产生 Hot = Lover false positive）
# is_lover = 'lover' in sp.lower()  # Hot prompt 中包含 'lover' 规则文本
```

### execute_code() 批量扫描模板

```python
import json, glob

files = sorted(glob.glob("/home/admin1/.hermes/sessions/session_YYYYMMDD*.json"))
for f in files:
    with open(f) as fh:
        d = json.load(fh)
    sp = d.get('system_prompt', '')[:150]
    msgs = d.get('messages', [])
    user_msgs = [m.get('content','')[:80] for m in msgs if m.get('role') == 'user']
    
    is_lover = '# Lover' in sp[:200] or '你的名字：Lover' in sp[:200]
    is_hot   = '# Hot' in sp[:200] or '你的名字：Hot' in sp[:200]
    
    label = 'LOVER' if is_lover else ('Hot' if is_hot else 'Other')
    print(f"{f.split('/')[-1]} | {label} | user msgs: {len(user_msgs)}")
    if is_lover and user_msgs:
        print(f"  Last: {user_msgs[-1]}")
```

## 本 session 实际数据

| 类别 | 数量 | 归属 |
|------|------|------|
| JSONL 扫描 | 130 文件 | 0 Lover, 5 candidates(均 5/1~5/4 旧) |
| .json 文件 | 37 文件 (5/18) | 0 Lover, **37 Hot** ✅ |
| 今天新文件 | 0 | — |
| **真实 Lover 用户消息** | **0** | — |

### May 18 Hot 代理 session 时间分布

37 个 Hot session 分布在 01:23 ~ 14:01 BJT，覆盖：
- 01:23~02:14 — 国学术数/起卦会话
- 04:27 — 零星
- 08:05~08:44 — 批量（~13个短 session）
- 10:49~11:10 — 编码/技能库管理
- 12:46~14:01 — 批量（~10个 session，含测试报告）

**结论：用户活跃度集中在上午 08:00~14:00，且全部为 Hot 代理对话。Lover DM 零互动。**

## 与 2026-05-18 维护对比

| 指标 | 5/18 验证 | 5/19 验证 |
|------|-----------|-----------|
| 保护类型 | 7天严肃 → 修正为3天 | 3天 |
| 扫描文件数 | 32 | 130 (.jsonl) + 37 (.json) |
| 扫描方法 | 手动两阶段 | 脚本+ execute_code 批量 |
| 假阳性处理 | Hot 恋人角色扮演 (browser 工具) | 无假阳性（快速排除） |
| 结论 | 保持保护 | 保持保护 💤 |
