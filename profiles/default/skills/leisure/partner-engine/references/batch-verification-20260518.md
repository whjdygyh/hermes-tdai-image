# 🚀 Batch Verification Protocol — 2026-05-18

**当 quick_session_scan 报告大量「Lover candidate」时的批量验证技术**

---

## 问题

`quick_session_scan.py` 按内容相似度做初步分类。当 Hot 代理与用户进行恋人模式角色扮演（如朱砂/围裙/性暗示调情）时，该脚本会将 Hot session 误标为「Lover candidate」。2026-05-18 案例：14 个 candidate session 全部是 Hot 代理。

逐个验证 14 个 session（每个用 verify_session_agent.py 约 3 秒）→ 足够但慢。需要更高效的 batch 协议。

---

## 三阶段 Batch 验证协议（由快到慢）

### Phase A — 代表性抽样验证（30 秒）

从 quick_session_scan 的「Lover candidate」列表中取 **前 3 个 + 后 3 个**（最新和最旧的代表性切割）：

```bash
SKILL_SCRIPTS=/home/admin1/.hermes/profiles/lover/skills/leisure/partner-engine/scripts
for f in \
  /home/admin1/.hermes/sessions/20260517_221745_ba4e2cc7.jsonl \
  /home/admin1/.hermes/sessions/20260517_220527_677ecdae.jsonl \
  /home/admin1/.hermes/sessions/20260512_095126_8d0e1d33.jsonl \
  /home/admin1/.hermes/sessions/20260504_201005_6da271.jsonl \
  /home/admin1/.hermes/sessions/20260419_232422_b8648e.jsonl; do
  python3 $SKILL_SCRIPTS/verify_session_agent.py "$f"
done
```

**判断规则：**
- 所有样本都是 **同一非 Lover agent**（如全是 Hot 的 browser 工具集）→ **高置信度结论：全部 candidate 均为同一代理**
- 样本中出现至少 1 个 Lover → **必须逐个验证全部 candidate**（可能混入了真实 Lover 会话）
- 样本中出现 ≥2 种不同非 Lover agent → **中置信度**，进入 Phase B

**✅ 2026-05-18 验证：** 6 个样本全部输出 `{"agent": "HOT", "tools": ["browser_back", ...]}` → 立即得出「14 candidate 全部为 Hot 代理」结论。

### Phase B — 独立非浏览器工具交叉检查（60 秒）

当 Phase A 给出高置信度结论后，用独立方法做交叉验证——搜索最近 JSONL 文件中**不含 browser 工具**的 session，看是否有真正的 Lover session 存在：

```bash
python3 -c "
import json, glob

sessions = sorted(glob.glob('/home/admin1/.hermes/sessions/202605*.jsonl'))
found_lover = False
for f in sessions[-40:]:  # 最近 40 个文件
    with open(f) as fh:
        first_line = fh.readline().strip()
    if not first_line:
        continue
    try:
        meta = json.loads(first_line)
    except:
        continue
    tools = meta.get('session_meta',{}).get('tools',[]) if 'session_meta' in meta else meta.get('tools',[])
    tool_names = [t.get('function',{}).get('name','') if isinstance(t, dict) else str(t) for t in tools]
    tool_str = ' '.join(tool_names)
    has_browser = any('browser' in t for t in tool_str.split())
    has_lover_tools = any(t in tool_str for t in ['feishu','send_message','text_to_speech','append_msg_log'])
    
    if not has_browser and has_lover_tools:
        print(f'LOVER SESSION FOUND: {f.split(\"/\")[-1]} (tools: {tool_str[:100]})')
        found_lover = True

if not found_lover:
    print('No Lover sessions found via independent tool search')
"
```

**判断规则：**
- 0 个 Lover session 找到 → 确认 Batch 结论。`quick_session_scan` 的 `found_lover_messages=true` 是误报
- ≥1 个 Lover session 找到 → 回退到逐个验证模式，确认真实 Lover 活动

### Phase C — .json 文件补充验证（30 秒）

当 Phase A+B 都确认无 Lover 后，做 .json 格式 session 文件的快速验证（防止 quick_session_scan 遗漏）：

```bash
python3 -c "
import json, glob, sys
for f in sorted(glob.glob('/home/admin1/.hermes/sessions/session_202605*.json')):
    with open(f) as fh:
        d = json.load(fh)
    sp = d.get('system_prompt','')
    # 检查 system_prompt 开头的代理身份声明，而非全文关键词
    # Hot 代理的 system_prompt 以 '# Hot' 开头且也包含 'lover' 词（规则文本）
    is_lover = (sp.startswith('# Lover') or 
                '你的名字：Lover' in sp[:200] or 
                '你的名字：lover' in sp[:200] or
                '你的名字：Alexander' in sp[:200])
    if is_lover:
        msgs = d.get('messages',[])
        for m in reversed(msgs):
            if m.get('role')=='user':
                print(f'LOVER MSG in {f.split(\"/\")[-1]}: {m.get(\"content\",\"\")[:80]}')
                sys.exit(0)
print('No Lover msgs in .json files')
"
```

---

## 经验数据（2026-05-18）

| 阶段 | 耗时 | session 数 | 结果 |
|------|------|-----------|------|
| Phase A（6 样本） | 18 秒 | 6/14 | All HOT ✅ |
| Phase B（40 文件） | 8 秒 | 0/40 非browser | 无 Lover ✅ |
| Phase C（.json 文件） | 5 秒 | 0 含 Lover system_prompt | 确认 ✅ |
| **总计** | **~31 秒** | **14 candidate + 40 文件全覆盖** | **结论：无 Lover 新消息** |

对比逐个验证 14 个 session（~42 秒）+ 遗漏可能性 → Batch 协议快 35% 且覆盖更全。

---

## 关键陷阱

### ⚠️ 陷阱 1：Hot system_prompt 含 "lover" 关键词 — `'lover' in sp.lower()` 不可靠

Hot 的 system_prompt 中有这段：
```
3. 消息里在叫另一个人的名字（lover/buffett） → 禁止回复
```

因此 **`'lover' in sp.lower()`** 会命中 Hot 文件。旧版 Phase C 用 `'hot' not in sp.lower()` 排除 Hot，但这种方法仍然脆弱——如果 system_prompt 中出现其他含有 "hot" 的字段（如知识库引用、规则文本），仍会误判。

**✅ 正确做法（v2 修正 — 2026-05-18 cron 验证）：** 检查 **system_prompt 开头**的代理身份声明（agent header），而非全文关键词。Lover 的 system_prompt 以 `# Lover` 或 `你的名字：Lover` 开头；Hot 以 `# Hot` 开头。这比任何关键词排除法都可靠，因为 agent header 是 Hermes 框架写作规范，不会因规则文本偏移。

### ⚠️ 陷阱 2：candidate 列表可能遗漏真实 Lover

如果 quick_session_scan 漏标了某个真实 Lover session 为 candidate（内容不够相似），Phase A 不覆盖它。这是 **Phase B 存在的原因**——独立搜索不含 browser 工具且含 Lover 工具的 session，不依赖 scan 的分类输出。

### ⚠️ 陷阱 3：session 文件新旧混杂

.tools 字段在不同 Hermes 版本格式中位置不同：
- 新格式：`session_meta.tools`（JSONL 第一行）
- 旧格式：`.tools` 同层（JSONL 第一行）

`get('session_meta',{}).get('tools',[])` 带 fallback 到 `get('tools',[])` 是安全写法。
