# 🚫 10分钟等待窗口 — 旧消息误判模式

> **记录于：** 2026-05-16
> **场景：** cron周六早安消息发送后，10分钟等待窗口检测用户秒回
> **问题：** 未做时间戳过滤，从 session JSONL 文件中读到昨天（5/15 12:27）的用户消息，误判为"用户刚刚回复"，提前终止等待。

---

## 问题描述

在实现 10 分钟等待窗口（§3.1）时，等待循环扫描 session 目录下的所有 JSONL 文件来检测新用户消息。

```python
# ❌ 错误的做法 — 会命中旧消息
jsonl_files = glob.glob(f"{SESSIONS}/*.jsonl")
for f in jsonl_files:
    content = open(f).read()
    if '"role": "user"' in content:
        print("用户有消息！")  # 一定触发 — 旧消息也在文件里
```

**后果：** 系统在等待了仅 15 秒（第一轮检查）后就退出等待循环，声称"用户回了消息"，实际命中的是昨天的对话记录。如果用户真的在这 10 分钟内回复了，后续几轮的检查全被跳过，真实回复被错过。

## 正确的实现模式

```python
import json, time, glob
from datetime import datetime, timezone

window_start = "2026-05-16T09:15:00+08:00"  # set dynamically

def parse_ts_to_epoch(ts_str):
    """Parse ISO timestamp like 2026-05-16T09:15:00+08:00 to epoch seconds."""
    # Handle timezone offset
    if '+' in ts_str:
        dt_str, tz = ts_str.rsplit('+', 1)
        tz_h, tz_m = int(tz[:2]), int(tz[2:])
        dt = datetime.fromisoformat(dt_str)
        offset = timezone.utc if tz_h == 0 else timezone(datetime.timedelta(hours=tz_h, minutes=tz_m))
        return dt.replace(tzinfo=offset).timestamp()
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00')).timestamp()

window_start_epoch = parse_ts_to_epoch(window_start)

for i in range(40):  # up to 10 minutes at 15s intervals
    time.sleep(15)
    
    jsonl_files = sorted(glob.glob(f"{SESSIONS}/*.jsonl"), key=os.path.getmtime, reverse=True)[:3]
    
    found_new = False
    for f in jsonl_files:
        # Only check files modified AFTER window_start (recent enough)
        if os.path.getmtime(f) < window_start_epoch:
            continue  # file hasn't been touched since before we started waiting
        
        with open(f) as fh:
            lines = fh.read().strip().split('\n')
        
        # Only check the LAST 20 lines — most recent conversation turns
        for line in reversed(lines[-20:]):
            try:
                entry = json.loads(line)
                if entry.get('role') != 'user':
                    continue
                msg_ts = entry.get('timestamp', '')
                if not msg_ts:
                    continue
                msg_epoch = parse_ts_to_epoch(msg_ts)
                if msg_epoch > window_start_epoch:
                    # ✅ This is a genuinely new message
                    found_new = True
                    break
            except (json.JSONDecodeError, ValueError):
                continue
        if found_new:
            break
    
    if found_new:
        print("🔥 用户有新消息！停止等待，准备回复。")
        # ... actual reply logic
        break
```

## 关键校验点

| 检查项 | 说明 |
|--------|------|
| ✅ 只扫描修改时间 > window_start 的文件 | 跳过所有未被写入过的旧文件 |
| ✅ 只解析最后20行 | 新消息只追加在文件末尾 |
| ✅ 逐行解析 JSON，提取 timestamp | 直接用 `grep` 或字符串匹配 `"role":"user"` 会命中任何历史消息 |
| ✅ 比较 timestamp > window_start | 必须转为可比较数值（epoch 秒），避免字符串比较歧义 |
| ✅ 只从旧到新扫描前3个文件 | 避免扫描整个目录下的全部 50+ 文件 |

## 🚨 v2 坑点：Session 文件 mtime 被系统刷新（2026-05-16 新增）

### 问题描述

在 2026-05-16 15:32 的等待窗口中，使用基于文件 mtime 的监控时发现了另一种 false-positive 模式：

```bash
# ❌ 第一版 —— 用 stat -c%Y 比较 mtime
for f in /home/admin1/.hermes/sessions/session_20260516*.json; do
  mtime=$(stat -c%Y "$f")
  if [ "$mtime" -gt "$WINDOW_START" ]; then
    echo "NEW SESSION: $f"   # ❌ 误触发！旧文件 mtime 被刷新
  fi
done
```

一个从 02:44 AM 创建的 session 文件，`stat -c%Y` 返回了约 `1778910594`（远大于 15:32 的 `1747380770`），触发 false-positive。原因是 Hermes 系统的 session 索引管理进程会在后台更新 session 文件的 mtime。

### 根因分析

| 文件系统属性 | 可靠性 | 原因 |
|------------|--------|------|
| `mtime` (修改时间) | ❌ 不可靠 | 系统后台进程（session 索引/元数据重建）会修改 session 文件的元数据 |
| `ctime` (状态变化时间) | ❌ 同上 | ctime = mtime 变化时也会更新，同样不可靠 |
| 文件内部 `timestamp` 字段 | ✅ 可靠 | 消息写入时的确切时间戳，不会被系统后台修改 |
| 文件名中的日期前缀 | ✅ 可靠 | `session_20260516_024400_*` 表示 02:44，不可变 |

### 正确的实现模式（v2 修正版）

```bash
# ✅ 使用 find -newermt（仍基于 mtime，但兼容不同文件系统）
WINDOW_START_EPOCH=$(date +%s)
new_files=$(find /home/admin1/.hermes/sessions/ -name '*.jsonl' -newermt @$WINDOW_START_EPOCH 2>/dev/null)
# 虽然 -newermt 也基于 mtime，但 find 的 y2038-safe 实现更可靠，
# 且只检查 JSONL 文件（比 session_*.json 更少被后台进程触碰）

# ✅ 终极可靠方案：读文件内部时间戳
python3 -c "
import json, time, glob
WINDOW_START = $WINDOW_START_EPOCH
for f in sorted(glob.glob('/home/admin1/.hermes/sessions/*.jsonl')):
    with open(f) as fh:
        lines = fh.read().strip().split('\n')[-20:]
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            if entry.get('role') == 'user':
                ts = entry.get('timestamp', 0)
                if ts > WINDOW_START:
                    print(f'FOUND: {f}', entry.get('content','')[:100])
        except:
            pass
"
```

### 实践建议

| 场景 | 推荐方法 | 理由 |
|------|---------|------|
| bash 监控脚本 | `find -newermt @$EPOCH` 配合 `*.jsonl` 文件 | 简单、可运行、误报率低 |
| Python 深度监控 | 逐行解析 JSONL，比较 `timestamp` 字段 | 唯一 100% 可靠方法 |
| 快速检查 `*.json` | 从文件名提取 $YYYYMMDD_HHMMSS 前缀 | 无需 IO，完全可靠 |

### ⚠️ 避免混合方法

不要混用：先用 `stat -c%Y` 判断文件新旧，再用 Python 解析内容。mtime 不可靠会直接阻断后续检查。**优先准则：要么完全依赖文件内部时间戳，要么完全依赖文件名**——不要把文件元数据和时间戳混在一起做 AND 判断。

---

## 为什么 session_search 不返回这些消息

`sessions_search` 工具按不同会话存储。旧 session 中的用户消息不会出现在今天的搜索结果中。但当手动扫描 JSONL 文件时，文件本身包含完整的、跨 session 的历史数据。**这就是为什么文件直接扫描比 search 更容易出现误报。**
