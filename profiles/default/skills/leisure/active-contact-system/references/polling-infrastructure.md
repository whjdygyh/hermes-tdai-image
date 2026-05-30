# 用户消息轮询基础设施

## 概述

本组件解决了主动联系系统最根本的「Phase B 断裂」问题：当用户回复了 cron 消息但 AI 不在线时，回复会被永久丢失。通过每5分钟轮询飞书API，将用户的新消息自动捕获到 `msg_log.json`，确保下次 AI session 启动时能读到完整的对话链。

## 核心架构

此 bot 部署在 **群聊** 中（而非与用户的 P2P 私聊）。这意味着轮询脚本无法通过简单的「用户 DM 消息列表」API 获取消息——必须采用**群聊消息轮询 + 已知用户过滤**的策略。

### 架构决策图

```
bot 在群聊中（非 P2P），没有直接的用户 DM chat_id
    ↓
方案A: 通过 P2P chat_type 过滤（❌ 失败，无 P2P 聊天）    [2026-05-12 已验证]
方案B: 通过群聊 + 已知用户 open_id 过滤（✅ 实际使用）
    ↓
poll_user_messages.py 实现方案B:
  1. GET /im/v1/chats → 列出 bot 所在的所有聊天（含群聊）
  2. 从配对文件 (feishu-pending.json) 加载已知用户 open_id
  3. GET /im/v1/messages?container_id={chat_id} → 拉取每个群聊的消息
  4. 只保留 sender.id 匹配已知用户 open_id 的消息
  5. 去重后写入 msg_log.json
```

### 关键洞察

- ⚠️ Feishu 「聊天列表」API (`GET /im/v1/chats`) 的返回项中**不包含** `chat_type` 字段（即使文档声称有）。因此不能依赖 `chat_type == "p2p"` 来过滤 DM 聊天。
- 群聊的 owner_id 可能等于用户的 open_id（用户创建的群），但消息发送者可以是群内任何人。
- 唯一可靠的方式：先从配对文件知道用户 open_id，然后在所有群聊消息中查找该 sender 的消息。

## 核心组件

### 1. 轮询脚本

**文件路径：** `~/.hermes/profiles/lover/scripts/poll_user_messages.py`

**工作原理：**
```
每5分钟运行一次 →
  1. 清除 http_proxy/https_proxy 环境变量（WSL 环境代理会阻拦 Feishu API）
  2. 从 .env 加载 FEISHU_APP_ID / FEISHU_APP_SECRET
  3. POST auth → 获取 tenant_access_token（注意 FEISHU_BASE 不含 /open-apis 后缀）
  4. GET /im/v1/chats → 列出所有聊天（群聊和 P2P，不限制类型）
  5. 从配对文件加载已知用户 open_id
  6. 对每个聊天：
     a. GET /im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size=50&sort_type=ByCreateTimeDesc
     b. 过滤 sender_type == "user" 的消息
     c. 进一步过滤 sender.id 匹配已知用户 open_id
     d. 跳过已见过的 msg_id（从 feishu_seen_message_ids.json 加载）
     e. 解析消息内容 JSON → 提取 text 字段
     f. 构建 msg_log 条目，追加到日志列表
     g. 更新 seen_ids 集合
  7. 若有新消息 → atomic write 保存 msg_log.json、poll_state.json、seen_ids
  8. 若无新消息 → 只更新 poll_state.json 的 last_updated 时间戳
```

**飞书API端点参考（均基于 FEISHU_BASE = "https://open.feishu.cn"）：**

| 用途 | 方法 | URL |
|:----|:----:|:----|
| 获取 token | POST | `/open-apis/auth/v3/tenant_access_token/internal` |
| 列出聊天 | GET | `/open-apis/im/v1/chats?page_size=50` |
| 获取消息 | GET | `/open-apis/im/v1/messages?container_id_type=chat&container_id={chat_id}&page_size=50&sort_type=ByCreateTimeDesc` |

**⚠️ FEISHU_BASE 陷阱：** `FEISHU_BASE` 必须设置为 `"https://open.feishu.cn"`，不能包含 `/open-apis` 后缀。完整的 API 路径在 URL 拼接时加上 `/open-apis/...`。否则会产生 `https://open.feishu.cn/open-apis/open-apis/...` 的双重复路径 → HTTP 404。

### 2. 从配对文件获取已知用户

**配对文件路径：** `~/.hermes/profiles/lover/platforms/pairing/feishu-pending.json`

**格式示例：**
```json
{
  "YP5K4GA": {
    "user_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
    "display_name": "...",
    "paired_at": "2026-04-24T10:30:00+08:00"
  }
}
```

**加载逻辑（`load_known_users()` 函数）：**
- 遍历多个预设路径（profile 级 pairing 目录 + 全局 pairing 目录）
- 提取所有 `user_id` 以 `"ou_"` 开头的条目
- 返回 open_id → True 的字典，供消息过滤使用

### 3. 去重逻辑（三层防护）

| 层级 | 机制 | 文件 | 说明 |
|:----:|:-----|:-----|:-----|
| 第一层 | 消息ID去重 | `feishu_seen_message_ids.json` | message_id → timestamp 映射，持久化存储 |
| 第二层 | 轮询状态 | `data/poll_state.json` | `last_processed_msg_id` 记录最新的已处理消息 |
| 第三层 | 消息内容去重 | 无（不依赖文本） | 同一 msg_id 不会重复处理，即使内容相同 |

**关键规则：**
- **永远基于 message_id 去重，不依赖内容文本** — 用户可能发两条内容完全相同的「好的」
- seen_ids 在内存中为 `set`，持久化为 `json` 文件（message_ids 字段）
- 新轮询开始时先加载 seen_ids → 新消息过滤 → 更新 seen_ids → 持久化
- 同一 session 内处理的多个 chat 共享同一个 `new_seen_ids` 集合（防止跨 chat 重复）

### 4. 状态文件

**`data/poll_state.json`：**
```json
{
  "last_processed_msg_id": "om_x100b6f143b3ae0a0b2bfc2fcd06f78b",
  "last_processed_time": 1778517855540,
  "last_updated": "2026-05-12T02:43:28+08:00"
}
```

### 5. Cron Job

| 属性 | 值 |
|:----|:----|
| 名称 | `msglog-poll` |
| 调度 | `*/5 * * * *`（每5分钟） |
| 交付模式 | `local`（不产生飞书通知） |
| 重复 | Forever |
| 当前状态 | ✅ 已创建并运行中 |

## ⚡ 已知陷阱和修复历史

### P1: FEISHU_BASE 路径重复（已修复）

**发现于：** 2026-05-12 首次运行

**症状：** `HTTP Error 404：https://open.feishu.cn/open-apis/open-apis/auth/v3/...`（URL 中 `open-apis` 重复）

**根因：** `FEISHU_BASE = "https://open.feishu.cn/open-apis"` 导致拼接 `f"{BASE}/open-apis/auth/v3/..."` 时产生 `open-apis/open-apis`。

**修复：** 将 `FEISHU_BASE` 改为 `"https://open.feishu.cn"`，所有 API 路径单独拼接 `/open-apis/...`。

### P2: P2P 聊天过滤无效（已修复）

**发现于：** 2026-05-12 第二次运行

**症状：** `get_bot_chat_ids()` 返回空列表，即使 bot 在 2 个群聊中。

**根因：** 代码过滤 `chat_type == "p2p"`，但 Feishu 聊天列表 API 返回项中**没有** `chat_type` 字段。所有聊天都被过滤掉。

**修复：** 移除 `chat_type == "p2p"` 过滤，接受所有 `chat_id`。然后通过已知用户 open_id 过滤消息。

**验证：**
```python
# API 返回示例（无 chat_type）：
{
    "chat_id": "oc_0bd840b91d01cf3a9afc27455d178750",
    "chat_status": "normal",
    "name": "一卷乾坤办公室",
    "owner_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386",
    # 注：无 "chat_type" 字段
}
```

### P3: `expanduser` 路径错误（已修复）

**发现于：** 2026-05-12 在 cron session 中运行

**症状：** `os.path.expanduser("~")` 返回 `/home/admin1/.hermes/profiles/lover/home` 而非 `/home/admin1`

**根因：** cron session 中 `HOME` 环境变量被设置为 profile 目录 (`~/.hermes/profiles/lover/home`)，导致 `~` 扩展错误。

**修复：** 所有路径使用硬编码绝对路径 `/home/admin1/.hermes/profiles/lover/...`，避免使用 `expanduser`。

**经验：** 在 WSL + cron 环境中，永远不要信任 `os.path.expanduser`。使用 `os.environ.get("HOME")` 检查当前值，或直接用绝对路径。

### P4: `is_user_message` 未使用参数（已修复）

**发现于：** 2026-05-12 运行中

**症状：** `TypeError: is_user_message() missing 1 required positional argument: 'token'`

**根因：** 函数签名为 `def is_user_message(msg, token)` 但调用处为 `is_user_message(msg)`。`token` 参数在函数体内未被使用。

**修复：** 移除未使用的 `token` 参数。

### P5: `new_seen_ids` 变量缺失（已修复）

**发现于：** 2026-05-12 路径修改后

**症状：** `NameError: name 'new_seen_ids' is not defined`

**根因：** 在 `main()` 函数中修改变量作用域时，`new_seen_ids = set()` 行被意外删除。脚本继续使用该变量但未定义。

**修复：** 在循环开始前恢复 `new_seen_ids = set()` 声明。

### 🔴 P6: 去重完全失效 — 变量传递错误（2026-05-12 发现，最隐蔽的bug）

**发现于：** 2026-05-12 第三次调试 — msg_log.json 膨胀到 169 条记录（预期约 45 条），且每次「检查新消息」都返回相同的老消息。

**症状：**
- `msg_log.json` 有 169 条记录，大量重复且仅有 31 个唯一 msg_id
- 轮询脚本每次运行都报告「找到新消息」，但这些消息内容与以前完全相同
- `feishu_seen_message_ids.json` 中有 113 个 msg_id，但 `msg_log.json` 只包含 31 个唯一 msg_id
- 用户说「你那个轮询一直在重复」

**根因：** `process_chat_messages()` 函数被调用时传递了**错误的变量**。

```python
# ❌ BUG（原代码）：
new_seen_ids = set()       # ← 创建空的集合
# ...
seen_ids = load_seen_ids() # ← 从文件加载的133个ID
# ...
new_entries = process_chat_messages(items, poll_state, new_seen_ids, user_ou)
#                                                   ^^^^^^^^^^^^
#                                                   传了空集合！
```

函数内部：
```python
def process_chat_messages(items, poll_state, seen_ids, user_ou):
    # ...
    for msg in reversed(items):   # from newest to oldest
        if msg_id in seen_ids:    # seen_ids 是空集合 → 永远不跳过！
            continue               # 永远不会执行此分支
        seen_ids.add(msg_id)      # 逐步填充空集合
```

**后果：** 每次运行都会重新处理所有消息（包括几个月前的），因为空集合永远不会包含任何 msg_id。重复消息持续追加，msg_log 失控膨胀。`feishu_seen_message_ids.json` 虽然每次都被写入，但**从未被实际用于去重**。

**修复：** 将第 2 行的 `new_seen_ids` 改为 `seen_ids`：

```python
# ✅ 修复后：
new_entries = process_chat_messages(items, poll_state, seen_ids, user_ou)
#                                                   ^^^^^^^^
#                                                   传了从文件加载的正确集合！
```

**为什么会写出这个bug？** 代码中有两个相似变量名：
- `seen_ids`（从文件加载 → 113 个 ID）
- `new_seen_ids`（累加新 ID → 初始为空）

当在 `main()` 的「处理循环」部分传参时，不小心引用了离调用处更近的 `new_seen_ids`。这是一个典型的**变量名作用域混淆**错误。

**事后修复：**
1. ✅ 修复变量传递（git patch）
2. ✅ 清理 msg_log.json：169→45 条记录（删除所有重复项）
3. ✅ 同步 seen_ids 文件：将日志中 31 个 msg_id 补入 seen_ids 文件（新增 20 个 ID）
4. ✅ 更新 poll_state.json：指向最新的已处理 msg_id

**经验教训（一般化）：**
- **命名区分度**：若两个变量一个是「已存在的数据」另一个是「待累加的数据」，确保命名易于区分。例如 `loaded_seen_ids` vs `pending_ids`，而非 `seen_ids` vs `new_seen_ids`
- **防御性检查**：`process_chat_messages()` 应`记录去重跳过的消息数`（如果 50 条消息中 48 条被跳过，说明去重正常工作；如果总是 0 跳过，说明去重失效）
- **定期检查**：`msg_log.json` 的记录数应与期望值大致匹配。如果出现 >2x 的异常增长，说明去重可能失效

### P7: msg_log.json 初始清理后 poll_state 未同步（已修复）

**发现于：** 2026-05-12 修复 P6 后

**症状：** 清理 msg_log.json 后，poll_state 的 `last_processed_msg_id` 仍指向 5/11 的旧消息（`om_x100b6f143b3ae0a0b2bfc2fcd06f78b`）。但日志中已有更新的 5/12 消息（如「你先别管我回的哪条了」）。

**修复：** 将 poll_state 的 `last_processed_msg_id` 更新为日志中最新 msg_id。同时将 `feishu_seen_message_ids.json` 补全为日志中包含的所有 msg_id。

**验证方法：** 修复后第 1 次 poll 运行应报告「无新消息」（所有已清理的消息都已标记为 seen）。

## ⚡ WSL fsync 陷阱（2026-05-12 发现）

**问题：** 在 WSL 环境下，`os.fsync(fd)` 调用后，实际的写入可能不会立即刷新到磁盘。Python 执行 `write → fsync → close` 后，紧接着用 `open().read()` 读到的仍是旧内容。这导致：
- 轮询脚本写入了新消息 → 返回成功
- 后续 AI session 用 `cat` 读 `msg_log.json` 时看到的是旧版本
- 用户的新消息实际已写入但不可见

**根因：** WSL 的文件系统层对 `fsync` 的支持不完全。`os.fsync(fd)` 返回成功但底层 `Ext4 → NTFS` 转换层未完全刷新。该行为在有缓存的文件读取接口中尤其明显。

**解决方案：atomic write + sync 命令**

```python
import os, json, tempfile, subprocess

def safe_write(filepath, data):
    """Atomic write: 先写 tmp 文件，再 mv 覆盖，最后 sync 磁盘"""
    tmp = tempfile.NamedTemporaryFile(
        dir=os.path.dirname(filepath),
        prefix='.tmp_',
        suffix='.json',
        delete=False,
        mode='w',
        encoding='utf-8'
    )
    try:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp.flush()
        tmp.close()
        os.replace(tmp.name, filepath)  # atomic on Linux (same filesystem)
        subprocess.run(['sync'], capture_output=True)  # flush disk cache
    except:
        os.unlink(tmp.name)
        raise
```

**关键点：**
- `tempfile.NamedTemporaryFile` 在目标目录创建临时文件（同一文件系统，`os.replace` 才原子）
- `os.replace()` 在 Linux 上是原子的（rename syscall）
- 最后的 `subprocess.run(['sync'])` 强制刷新所有磁盘缓存 — 这是绕过 WSL fsync bug 的关键
- 如果仍读不到 → 用 `write_file` 工具替代（该工具绕过了 Python 的 IO 缓存）

## ⚡ 脚本编写清单

在修改或重写 `poll_user_messages.py` 时，检查以下要点（全部在此 session 中失败过）：

- [ ] `FEISHU_BASE` 设为 `"https://open.feishu.cn"`（无 `/open-apis` 后缀）
- [ ] 路径全部使用绝对路径（`/home/admin1/.hermes/profiles/lover/`），避免 `expanduser`
- [ ] 清除 `http_proxy` / `https_proxy` 环境变量（WSL 默认配置拦截外部 API）
- [ ] 不使用 `chat_type` 字段过滤聊天类型（API 不一定返回该字段）
- [ ] 从配对文件加载已知用户 open_id 用于群聊消息过滤
- [ ] `is_user_message()` 函数不要有未使用的参数
- [ ] `seen_ids`（从文件加载）和 `new_seen_ids`（新发现 ID）**不要混淆** — 传递 `seen_ids` 给 `process_chat_messages()` 用于去重
- [ ] 使用 atomic write (tmp file + os.replace + sync) 确保数据安全
- [ ] 消息去重使用 `message_id`，而非内容文本
- [ ] 群聊消息中需要解析 `body.content` 的 JSON 结构提取 text 字段
- [ ] 创建子任务后执行「即创建即验证」确认 `Script:` 行存在

## 与主 session 的集成

每次 AI session 启动时（包括 cron session 和用户主动发起的 session），必须执行以下协议：

```
Step 1: cat ~/.hermes/profiles/lover/data/msg_log.json  （验证最新内容）
Step 2: session_search 查最近交互
Step 3: 基于完整上下文回复用户
Step 4: 用 write_file 工具将本回合对话追加写入 msg_log.json
```

**重要：**
- 使用 `cat` 而非 `read_file`（`read_file` 有缓存bug，可能返回旧版本）
- 追加写入时使用 `write_file` 工具，而非 Python `open().write()`（绕过 WSL IO 缓存）
- 每回合都追加，包括用户消息和 bot 回复

## 文件位置速查

| 文件 | 路径 | 用途 |
|:----|:-----|:-----|
| 轮询脚本 | `~/.hermes/profiles/lover/scripts/poll_user_messages.py` | 每5分钟轮询飞书API |
| 消息日志 | `~/.hermes/profiles/lover/data/msg_log.json` | 完整的 bot+用户对话历史 |
| 轮询状态 | `~/.hermes/profiles/lover/data/poll_state.json` | 记录最后一次处理的消息ID |
| 已见消息ID | `~/.hermes/profiles/lover/feishu_seen_message_ids.json` | 持久化消息去重 |
| 配对文件 | `~/.hermes/profiles/lover/platforms/pairing/feishu-pending.json` | 获取已知用户 open_id |
| 活动状态 | `~/.hermes/profiles/lover/data/active_contact_state.json` | 主动联系系统状态 |
| 协议文档 | `~/.hermes/skills/leisure/active-contact-system/references/cron-message-response-protocol.md` | 上下文重建协议 |

## 验证方法

```bash
# 1. 手动触发一次轮询
cd /home/admin1/.hermes/profiles/lover && unset http_proxy https_proxy && python3 scripts/poll_user_messages.py

# 2. 检查 msg_log 是否有最新消息
cat /home/admin1/.hermes/profiles/lover/data/msg_log.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{len(d[\"log\"])} entries'); [print(f'{e[\"time\"]}: {e[\"content\"][:60]}') for e in d['log'][-5:]]"

# 3. 验证 poll_state 是否更新
cat /home/admin1/.hermes/profiles/lover/data/poll_state.json

# 4. 检查配对文件中的已知用户
cat /home/admin1/.hermes/profiles/lover/platforms/pairing/feishu-pending.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'{k}: {v[\"user_id\"]}') for k,v in d.items()]"

# 5. 查看 seen_ids 统计
cat /home/admin1/.hermes/profiles/lover/feishu_seen_message_ids.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Total seen IDs: {len(d.get(\"message_ids\",{}))}')"

# 6. 列出 bot 所在的所有聊天
# 通过测试脚本（需要自行创建）调用 GET /im/v1/chats

# 7. 验证去重是否正常工作（关键检查！）
cat /home/admin1/.hermes/profiles/lover/data/msg_log.json | python3 -c "
import sys,json
d=json.load(sys.stdin)
entries = [e for e in d['log'] if e.get('msg_id')]
msg_ids = set(e['msg_id'] for e in entries)
print(f'Total entries: {len(entries)}')
print(f'Unique msg_ids: {len(msg_ids)}')
print(f'Duplicate %: {(1 - len(msg_ids)/len(entries))*100:.1f}%' if entries else 'No entries')
if len(msg_ids) < len(entries) * 0.8:
    print('⚠️  WARNING: High duplicate ratio — dedup may be broken again!')
else:
    print('✅  Dedup looks healthy')
"
```
