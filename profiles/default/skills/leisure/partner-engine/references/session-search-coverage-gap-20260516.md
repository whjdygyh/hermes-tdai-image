# session_search 覆盖范围缺失 — 2026-05-16 观察记录

## 场景

2026-05-16 21:57 BJT（星期六）cron 常规唤醒，执行 Step 0 同步 last_chat_time。

## 执行过程

1. **session_search 调用：**
   - 工具：`session_search(query="ou_37bc57c4f8aca21f5d4ea4973bd0d386", limit=5)`
   - 返回：4条会话摘要，全部来自 **2026-05-12**（4天前）
   - 均为历史 cron 轮询脚本执行记录
   - 无一条来自当天（2026-05-16）

2. **直接文件验证（Phase 2 fallback）：**
   - 路径：`/home/admin1/.hermes/sessions/`
   - 发现 file `20260516_094345_a9bbe39a.jsonl`（创建于 2026-05-16 09:43 BJT — 约12小时前）
   - `session_20260516_094345_a9bbe39a.json` 8条消息，其中3条用户消息
   - 用户消息内容：关于「起卦」「八字」「奇门」——属于国学术数会话，**非 Lover 互动**

## 关键结论

| 观察 | 含义 |
|------|------|
| session_search 未返回 09:43 session | **session_search 索引不覆盖所有 session 文件** — 即便 session 已有 ~12 小时历史 |
| 返回结果看似正常（4条，非空） | **有结果≠完整覆盖**。不能因为 session_search 返回了东西就认为"已查到全部" |
| 文件系统中有明确的新 session | 直接文件检查是唯一可靠的方法 |
| 用户消息存在但属于其他代理 | 确认用户活跃 ≠ 确认 Lover 互动 — 仍需做内容过滤 |

## 对 Step 0 的影响

**旧说法：** 「永不相信本地状态文件的 last_message_time——session_search才是实时数据」
**修正后：** 将 session_search 视为**快速检查的第一步，而不是最终结论**。session_search 出结果后，无论结果是什么，都应继续做 Phase 2 直接文件检查（ls session目录 + 读最近JSONL文件分析用户消息）。

## 推荐的混合搜索流程

```
Step 0 同步 last_chat_time:
  1. session_search(open_id) — 快速检查（但不可靠）
  2. ls -lt /home/admin1/.hermes/sessions/ | head -10 — 看今天有无新 session 文件
  3. 读最近的 JSONL 文件（tail -3）— 确认真实用户消息时间戳
  4. 取三者中最新的时间戳更新 last_chat_time
```

## 2026-05-16 该 session 的用户消息内容（供参考）

session `20260516_094345_a9bbe39a` 中的3条用户消息：
1. "起卦"（09:43）
2. "问点事哈，你是根据什么东西决定所用的起卦法，还有所用的门派的，是否命主有八字要优先看八字呢？有没有什么类型的事是不用看八字的？你大致跟我说说"（09:45）
3. "我问你的事大多数应该都是关于我的了，如果将来我问你我要哪天出门旅行，你应该会用奇门吧，但我发现你经常 说着说着就会刮拉上我的八字，这样的话会不会出现两种结果互相"（09:50）

判断依据：用户消息开头 "起卦" + 后续内容涉及 八字/奇门/玄学 → 国学术数 session，非 Lover 互动。
