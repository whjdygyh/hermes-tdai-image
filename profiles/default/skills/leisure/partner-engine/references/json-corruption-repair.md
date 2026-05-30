# JSON状态文件ASCII引号腐蚀修复指南

> **真实案例：** 2026-05-17 17:02 BJT — active_context.json notes 字段中「"还没吃午饭"」的双引号导致 `json.loads()` 在 pos=1015 处报错。
> 所有后续 cron 脚本无法读取状态文件，直到人工修复。

## 根本原因

Lover 的状态文件（active_context.json / emotional_state.json / msg_log.json）中，
**notes / context 字段**存储的是自然语言文本，可能包含**未转义的 ASCII 双引号 `"`**。

JSON 规范中，字符串内部的 `"` 必须写作 `\"`。如果中文文本中直接出现 `"`（例如用户提到的「"还没吃午饭"」），
则 `json.loads()` 会将其解释为字符串的结束标记，导致后续文本解析失败。

## 探测方法

```bash
# 1. 尝试解析文件，找出错误位置
python3 -c "
import json
with open('/path/to/active_context.json', 'r', encoding='utf-8') as f:
    content = f.read()
try:
    json.loads(content)
    print('JSON OK')
except json.JSONDecodeError as e:
    print(f'Error at pos {e.pos}: {e.msg}')
    print(f'Context: ...{content[max(0, e.pos-40):e.pos+40]}...')
"
```

输出示例：
```
Error at pos 1015: Expecting ',' or '}' or ']'
Context: 安迪最后消息内容为\u201c"还没吃午饭"\u201d        
```

## 修复方法

### 方法一：全角引号替换（推荐）

ASCII 双引号 → 全角中文引号，因为全角引号在 JSON 字符串中不需要转义。

```python
import json

with open('/tmp/active_context.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 替换 ASCII 双引号为全角引号
# 注意：这只替换那些在 JSON 字符串值内部的双引号
# 如果 JSON 本身就包含字符串边界，不能简单全局替换
# 安全策略：定位错误具体位置，手动修复上下文

# 安全方式（2026-05-17 验证有效）：
# 识别出「"还没吃午饭"」这类中文语境中的 ASCII 引号对
# 用全角替换
fixed = raw.replace('"还没吃午饭"', '\u201c还没吃午饭\u201d')

# 验证
data = json.loads(fixed)
print(f"✅ Fixed! notes = {data.get('notes', 'N/A')[:60]}...")

# 写回
with open('/path/to/active_context.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### 方法二：逐字符扫描（用于未知位置的引号）

```python
import json

with open('/tmp/broken.json', 'r', encoding='utf-8') as f:
    raw = f.read()

# 更通用的方法：用 json.JSONDecoder.raw_decode() 定位
# 然后手动在错误位置前补转义
# 但更简单的方式是：把字符串值中看起来像"中文引号"的 ASCII 双引号替换为全角

import re

def fix_chinese_quotes(text):
    """替换中文语境中的 ASCII 双引号为全角"""
    # 中文和后跟 ASCII 双引号的模式：汉字+ASCII 双引号
    # 例如：的" → 的\u201c
    text = re.sub(r'([\u4e00-\u9fff\u3000-\u303f\uff00-\uffef])"([\u4e00-\u9fff])', r'\1\u201c\2', text)
    text = re.sub(r'([\u4e00-\u9fff\u3000-\u303f])"([^\",}\\]]{1,10})"', r'\1\u201c\2\u201d', text)
    return text

fixed = fix_chinese_quotes(raw)
try:
    data = json.loads(fixed)
    print("✅ Fixed automatically!")
except json.JSONDecodeError as e:
    print(f"❌ Still broken at pos {e.pos}")
    print(f"Context: ...{fixed[max(0, e.pos-40):e.pos+40]}...")
```

## 预防策略

| 层面 | 措施 |
|------|------|
| **脚本写入** | 使用 `json.dumps()` 自动转义而非字符串拼接。所有 Python 脚本必须通过 json 库序列化后再写文件 |
| **manually_patch 调用** | 如果使用 `sed` / `echo` 写文件，必须确保值被 `json.dumps()` 处理过。绝对禁止用 `echo "{...}" > file.json` |
| **读取端防御** | 所有 state 文件读操作必须 try/except 包 `json.loads()`。解析失败 → 记录日志但继续执行（用默认值兜底），不崩溃 |
| **定期巡检** | 每次 cron 醒来时先做一次 state 文件完整性检查（全部 `json.loads()` 验证），发现损坏立即修复 |

## 相关文件

- `active_context.json` — notes 字段最容易出现中文引号
- `emotional_state.json` — notes / context 字段
- `last_outgoing.json` — last_message 字段（消息原文可能含引号）
- `msg_log.json` — messages[].content 字段
