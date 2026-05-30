# Feishu Local Data Stores — 飞书本地数据存储架构

> 当需要访问飞书本地缓存的聊天记录、日志或配置文件时，此文档提供已知的存储路径和可读性评估。

## 环境

- **Windows 飞书客户端版本**: 7.68.5 (Electron 应用)
- **访问方式**: WSL 通过 `/mnt/c/` 挂载 Windows 文件系统

## 存储路径

### 主数据目录

```
C:\Users\<username>\AppData\Local\Feishu\
```

| 子目录 | 内容 | 可读性 |
|--------|------|--------|
| `7.68.5/assets/` | 前端静态资源(emoji, audio, image) | 资源文件，非用户数据 |
| `7.68.5/iron/` | 媒体缓存(图片/音频) | 部分可读，但非结构化 |
| `7.68.5/webcontent/` | 子应用前端包(larklet) | config/manifest JSON，非聊天数据 |
| `7.68.5/launch/` | 启动配置 | 程序配置 |
| `7.68.5/log/` | 客户端日志 | ✅ 可读的 .log 文件，但仅含程序/性能日志 |
| `User Data/Cache/program/` | 程序缓存 | 二进制，不可直接读 |
| `User Data/config/` | 用户配置 | 需检查具体文件 |

### aha_doctor 子组件

```
C:\Users\<username>\AppData\Local\aha_doctor\Feishu\
```

| 子目录 | 内容 | 可读性 |
|--------|------|--------|
| `config/` | 安全/沙箱配置 | 程序配置 |
| `log/` | aha_doctor 组件日志 | ✅ 可读 .log，纯系统日志(启动/模块加载) |
| `event/` | 事件缓存 | ⚠️ .db2 文件 — **BTrieve/Pervasive SQL 专有格式**，非标准 SQLite |
| `dump/` | 崩溃转储 | 二进制 |

### .db2 文件格式

位于 `aha_doctor/Feishu/event/` 目录下的 `.db2` 文件：
- `applog.cache2` — 应用事件缓存
- `applog.db2` — 主事件数据库
- `session.db2` — 会话数据
- `custom.db2` — 自定义数据
- 格式为 **BTrieve/Pervasive.SQL 专有格式**，非 SQLite/JSON/CSV
- 不是飞书聊天记录 — 是 aha_doctor 安全组件的内部事件追踪

## 关键发现

### 飞书聊天记录不在 Windows 客户端本地存储

**飞书(Feishu)作为 Electron/Chromium 应用，聊天记录存在服务器端，本地不做持久化存储。** 这是大部分 SaaS 企业IM应用的共同设计。

本地仅有的缓存：
- 媒体文件（图片/语音）的临时缓存 (`iron/`)
- 前端静态资源的浏览器缓存
- aha_doctor 事件追踪（非聊天数据）

### ⭐ Hermes Agent 本地会话存储 (会话级聊天记录的完整副本)

**2026-05-15 发现：Hermes Agent 在本地存储了所有对话会话的完整 JSON 文件。** 作为飞书机器人，我们每次的对话都被记录在 Agent 的会话目录中。

#### 位置和规模

```
~/.hermes/sessions/
```

| 指标 | 数值 |
|:----|:-----|
| 总会话文件 | ~733 个 |
| 其中飞书会话 | ~398 个 |
| 总消息量 | ~37,000+ 条 |
| 磁盘占用 | ~120MB |
| 时间跨度 | 4月16日~至今 |

#### 文件结构

**主会话文件：** `session_<日期>_<时间戳>_<hash>.json`

每个文件包含一次完整会话的全部消息（`messages` 数组），角色包括 `user`（用户消息）、`assistant`（机器人回复）、`tool`（工具调用记录）：

```json
{
  "session_id": "20260515_005710_045530",
  "platform": "feishu",
  "model": "deepseek-v4-flash",
  "provider": "deepseek",
  "message_count": 92,
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "tool", "content": "..."}
  ]
}
```

**会话索引文件：** `sessions.json`

```
agent:main:feishu:dm:oc_xxx:omt_xxx → {session_id, ...}
```

键格式：`agent:main:feishu:dm:{user_id}:{thread_id}`，其中：
- 无 `omt_` 前缀 → 主DM会话
- 有 `omt_` 前缀 → 子话题/thread 会话

**日志文件：** `*.jsonl` 文件（如 `20260514_111616_c07c41e7.jsonl`）
- 行格式的 JSON 日志，约 140KB 大小
- 包含会话流转记录

#### 平台分布

| 平台 | 会话数 | 说明 |
|:----|:------|:-----|
| `feishu` | 398 | 飞书聊天会话（主要） |
| `cli` | 80 | 终端 CLI 会话 |
| `tui` | 74 | TUI 控制台会话 |
| `cron` | 4 | 定时任务触发会话 |
| `curator` | 2 | 技能库自动化会话 |
| `?` | 163 | 早期/不完整/快照文件（message_count=0） |

#### 使用方式

```bash
# 1. 列出所有会话
ls -lh ~/.hermes/sessions/session_*.json | wc -l

# 2. 看最近的会话
ls -lt ~/.hermes/sessions/session_*.json | head -10

# 3. 读取索引找特定会话
cat ~/.hermes/sessions/sessions.json | python3 -m json.tool | grep "oc_xxx"

# 4. 读取会话内容
cat ~/.hermes/sessions/session_xxx.json | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Session: {d[\"session_id\"]}, {d[\"message_count\"]}msgs, {d[\"platform\"]}')
for m in d['messages']:
    print(f'  [{m[\"role\"]}] {m[\"content\"][:100]}...')
"
```

#### **注意：当前进行的对话在飞书端还在进行中，尚未完全写入本地会话文件。** 会话文件是在对话结束后（或上下文压缩时）完整保存的。

### 可用的替代数据源

| 数据源 | 位置/方式 | 包含什么 |
|--------|-----------|----------|
| **Hermes 本地会话文件** ⭐ | `~/.hermes/sessions/session_*.json` | **完整对话历史**（所有角色，含工具调用） |
| **Hermes session_search** | `session_search()` 工具 | 本智能体与用户的对话记录（通过文件系统搜索） |
| **伴侣引擎 msg_log.json** | `~/.hermes/profiles/lover/data/msg_log.json` | 伴侣引擎(Bot)主动发送的消息日志 |
| **Feishu Open API** | `GET /open-apis/im/v1/messages` | 完整的飞书消息历史（需API调用） |
| **Feishu Webhook/WS** | feishu-websocket-events 技能 | 实时事件流 |

### 实际建议

1. **查找历史聊天记录 → 优先使用 Hermes 本地会话文件** `~/.hermes/sessions/session_*.json`
2. **实时/当前对话 → 用 session_search 工具**（因为当前对话尚未写入文件）
3. **伴侣引擎 msg_log.json** 仅记录 bot→user 的主动消息，不包含 user→bot 的回复
4. **不要依赖 Windows 飞书客户端本地文件** — 客户端不保存完整历史
