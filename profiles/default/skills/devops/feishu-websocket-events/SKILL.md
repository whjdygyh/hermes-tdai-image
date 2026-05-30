---
name: feishu-websocket-events
title: Feishu WebSocket Event Subscription
description: 飞书/飞书WebSocket(长连接)事件订阅 — 无需公网URL，实时接收评论、消息等事件通知
category: devops
---

# Feishu WebSocket Event Subscription

## Overview

飞书支持**长连接(WebSocket)**模式接收事件，**不需要公网HTTP回调URL**。应用主动发起WebSocket出站连接到飞书服务器，实时接收事件推送。

## When to Use

- 需要实时接收飞书事件（文件评论、消息等）
- 服务器没公网IP/端口被防火墙封锁
- 出站WebSocket连接可用（走443端口）

## Setup Steps

### 1. 飞书开放平台配置

1. [飞书开放平台](https://open.feishu.cn) → 你的应用 → **事件与回调**
2. 连接方式选：**使用长连接接收事件**
3. 添加需要的事件（如 `drive.notice.comment_add_v1`）
4. 添加所需权限 → **发布新版本**
5. 回调地址URL留空（长连接不需要）

### 2. 安装SDK

```bash
pip3 install lark-oapi
```

自动安装 `lark-oapi` + `websockets` 依赖。

### 3. 编写事件监听脚本

```python
from lark_oapi import EventDispatcherHandler, LogLevel
from lark_oapi.ws import Client as WSClient

APP_ID = "your_app_id"
APP_SECRET = "your_app_secret"

def handle_comment_add(event):
    print(f"收到评论事件! type={event.header.event_type}")
    print(f"数据: {event.event}")  # dict格式

# 对SDK没预置handler的事件类型用 register_p2_customized_event
handler = EventDispatcherHandler.builder("", "") \
    .register_p2_customized_event(
        "drive.notice.comment_add_v1",
        handle_comment_add
    ) \
    .build()

ws_client = WSClient(
    app_id=APP_ID,
    app_secret=APP_SECRET,
    event_handler=handler,
    log_level=LogLevel.INFO,
    auto_reconnect=True  # 自动断线重连
)

# 阻塞启动 - 必须从同步上下文调用
ws_client.start()
```

### 完整生产版脚本（带日志+信号文件+异常处理）

参见 `references/album-comment-workflow.md` 或 `/tmp/feishu_ws_listener.py`（部署版）。

关键特性：
- 日志写入 `/tmp/feishu_events.log`（不受上下文压缩影响）
- 收到事件后写信号文件 `/tmp/feishu_event_received.signal`
- 主进程通过检测信号文件得知有新评论
- 自动重连 + 完整异常堆栈

## Customized Events

SDK `EventDispatcherHandlerBuilder` 有大量预置的 `register_p2_*` 方法。如果目标事件类型不在预置列表中（如 `drive.notice.comment_add_v1`），用 **`register_p2_customized_event(event_type, callback)`**。

```python
handler = EventDispatcherHandler.builder("", "") \
    .register_p2_customized_event("drive.notice.comment_add_v1", my_handler) \
    .build()
```

## 常见事件类型

| 事件 | 类型字符串 | 适用文件类型 |
|------|-----------|-------------|
| 新文件评论 | `drive.notice.comment_add_v1` | doc/docx/bitable/sheets + **图片(file) ✅**（需@机器人） |
| 收到消息 | `im.message.receive_v1` | DM/群聊 |
| Reaction添加 | `im.message.reaction.created_v1` | 消息 |
| Reaction移除 | `im.message.reaction.deleted_v1` | 消息 |

### ⚠️ 重要条件：仅当@机器人时触发

**2026-05-06 实测确认：`drive.notice.comment_add_v1` 会对图片文件触发，但仅在评论中@机器人时。**

关键行为：
- 用户在相册照片评论中 **@机器人** → WebSocket收到事件 (`is_mentioned=true`)
- 用户评论**不@机器人** → 事件**不会触发**
- 评论API (`GET /drive/v1/files/{token}/comments?file_type=file`) 可以正常读取图片评论

## 数据读取

收到 `drive.notice.comment_add_v1` 事件后，调用API获取完整评论内容：

```bash
GET /open-apis/drive/v1/files/{file_token}/comments?page_size=10&file_type=file
```

**⚠️ 必须带 `file_type=file` 参数**，否则对图片文件返回空。

返回的评论数据结构：
```json
{
  "items": [{
    "comment_id": "7636799323993934784",
    "user_id": "ou_xxx",
    "reply_list": {
      "replies": [{
        "reply_id": "7636799324009008071",
        "content": {
          "elements": [{
            "text_run": {"text": "评论内容"},
            "type": "text_run"
          }]
        },
        "user_id": "ou_xxx"
      }]
    }
  }]
}
```

## 🚨 关键限制：不能创建新评论，只能回复已有评论

**2026-05-07 实测确认：图片文件不支持程序化创建新评论线程。**

```bash
# ❌ 以下API对图片文件失败
POST /drive/v1/files/{file_token}/comments?file_type=file
# → code: 99992402 "field validation failed: file_type is optional, options: [doc,docx]"
```

即：
- `POST /drive/v1/files/{token}/comments` — 创建新评论 → ❌ 仅doc/docx可用，图片不行
- `POST /drive/v1/files/{token}/comments/{id}/replies` — 回复已有评论 → ✅ 图片可用
- `GET /drive/v1/files/{token}/comments` — 读取评论 → ✅ 图片可用（需file_type=file）

**结论：旧配文/故事无法通过API批量写到新照片上。** 用户可以在飞书UI里手动评论，API只能回复用户已创建的评论。

替代方案（详见 `references/album-comment-workflow.md` → "无法批量写入配文的变通方案"）：

> ⚠️ **用户偏好：一天一天写（渐进式），不接受一次性批量写入。** 每次生新图时，在飞书DM发图+配文。不要试图用脚本一次性写入全部旧配文。

1. 在相册文件夹内新建一个飞书文档，把照片→配文映射写进去
2. 重新生成自包含HTML相册（带配文），上传到文件夹
3. 每天用TTS读一条配文发给用户DM
4. 用PATCH API改文件标题（有限，只能放短描述）
5. 生图后直接飞书DM发照片+配文

> ⚠️ 用户偏好"一天一天写"（渐进式），不接受一次性批量写入。

## 回复评论API

对图片文件的**已有**评论进行回复：

```bash
POST /open-apis/drive/v1/files/{file_token}/comments/{comment_id}/replies?file_type=file
Content-Type: application/json

{
  "content": {
    "elements": [{
      "text_run": {"text": "回复内容"},
      "type": "text_run"
    }]
  }
}
```

**关键坑：`content` 必须作为 JSON 对象发送，不是 JSON 字符串！**
- ✅ 正确：`"content": {"elements": [...text_run...]}`
- ❌ 错误：`"content": "{\"elements\": [...]}"`（返回 code 9499）

## 给用户开权限

相册文件夹需要给用户授予 `full_access` 权限，用户才能在照片上写评论：

## 相关参考

- `references/local-data-stores.md` — 飞书本地数据存储全览：Windows客户端 + **Hermes Agent本地会话JSON文件**（`~/.hermes/sessions/session_*.json`，398个飞书会话，37k+消息）
- `references/album-comment-workflow.md` — 完整监听脚本 + 评论区回复交互工作流
- `references/feishu-drive-upload-all.md` — 飞书云盘文件上传 upload_all API 详情（生图后自动存相册用）

## Pitfalls

1. **不要从异步上下文调用**：`ws_client.start()` 自带事件循环，必须从同步函数调用，不能用 `async def` + `await`。
2. **长连接没有订阅ID**：SDK自动处理认证，不需要手动传subscription_id。
3. **发布版本**：配置完事件和权限后必须**发布新版本**，否则事件不会推送。
4. **防火墙**：出站到 `wss://msg-frontier.feishu.cn:443` 必须放行。
5. **不要轮询(polling)**：用户明确禁止主动扫API查评论。用长连接被动接收事件。
6. **💡 评论触发条件**：`drive.notice.comment_add_v1` 对图片文件仅在**@机器人**时触发。不带@的评论不产生事件。回复评论API中 `content` 必须是 JSON**对象**（不是字符串）。

## 验证连接

```bash
timeout 10 python3 your_script.py 2>&1 | grep "connected to"
# 看到 "connected to wss://msg-frontier.feishu.cn/ws/v2..." 即成功
```

## 生产化

长连接脚本应作为systemd服务或后台进程长期运行。示例systemd service：

```
[Unit]
Description=Feishu Event Listener
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/listener.py
Restart=always
RestartSec=10
User=your_user

[Install]
WantedBy=multi-user.target
```
