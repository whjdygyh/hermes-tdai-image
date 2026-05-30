# 飞书云盘文件评论 API 实战笔记

## 场景
用户（安迪）在飞书云盘相册文件夹的图片上留言评论，需要助手能感知并回复这些评论。

## ⚠️ 最终结论（2026-05-06）：此方案不可行

**飞书云盘图片文件不支持评论功能。** 所有尝试均失败：

1. `drive.notice.comment_add_v1` WebSocket 事件**不会为图片文件触发**（此事件仅作用于文档类）
2. `GET .../comments?file_type=file` 对所有图片返回 `items: []`（空数组）
3. `POST .../comments` 对 `file_type=file` 报错，仅支持 `doc/docx`

**替代方案**：用户在飞书 DM 中与助手直接沟通。

## 核心限制：无公网 URL
服务器在 NAT 后，所有端口被防火墙封锁，Cloudflare Workers 域名国内不可达。

## 🚨 用户强制偏好（2026-05-06 — 重要！）
**用户明确拒绝轮询方案**。原话："我不想让你辛苦去主动扫，我觉得他一定能通知到你才对。"

**这意味着**：
- ❌ **不要提定时轮询（cron polling）** — 用户不喜欢被动扫描方案
- ❌ **不要提 "方案A/方案B"** 这类工程分类
- ✅ 优先探索飞书原生通知机制，找到无需公网 URL 的事件接收方式
- ✅ 用户已在开放平台配置 `drive.notice.comment_add_v1` 事件并发布

## 事件订阅历史

### 尝试：WebSocket 长连接
- 成功连接 `wss://msg-frontier.feishu.cn/ws/v2`
- 注册 `register_p2_customized_event("drive.notice.comment_add_v1", handler)`
- 用户留言后：**零事件到达** ✅ 确认此事件不为图片触发

### 已配置
- 事件类型: `drive.notice.comment_add_v1`（"有新文档评论或回复通知"）
- 状态: 已配置+已发布
- 回调 URL: **留空**（因无公网地址）

## 读评论 API ✅ 已确认可用（但仅对图片返回空）

### GET 读取评论列表
```
GET https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/comments
  ?page_size=10
  &file_type=file          # ← 关键！对图片/普通文件必须用 file_type=file
Authorization: Bearer {tenant_access_token}
```

**重要发现**：
- `file_type=file` 适用于图片、普通文件等非文档类文件 ✅
- `file_type=doc` / `file_type=docx` 仅适用于飞书文档 ❌（对图片返回 `not exist`）
- `file_type=image` 会报 `field validation failed` ❌（不存在的枚举值）
- **但即使 API 可用，返回始终为空** — 因为图片根本就没有评论存储

### 返回格式
```json
{
  "code": 0,
  "data": {
    "has_more": false,
    "items": [],
    "page_token": "0"
  }
}
```

### 扫描整个文件夹的评论
```bash
# 1. 列出文件夹所有文件
curl -X GET "https://open.feishu.cn/open-apis/drive/v1/files?page_size=50&folder_token=${FOLDER_TOKEN}" \
  -H "Authorization: Bearer $TOKEN"

# 2. 对每个 file_token 调 comments 接口（file_type=file）
for TOK in $ALL_TOKENS; do
  curl -X GET "https://open.feishu.cn/open-apis/drive/v1/files/${TOK}/comments?page_size=5&file_type=file" \
    -H "Authorization: Bearer $TOKEN"
done
```
**实测结果**：81 张图片无评论时返回空数组，API 正常但无数据。

## 写评论 API ❌ 仅限文档
```
POST https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/comments
  ?file_type=doc           # 仅支持 doc/docx
Content-Type: application/json
Authorization: Bearer {token}

{"content": "[[{\\\"tag\\\":\\\"text\\\",\\\"text\\\":\\\"评论内容\\\"}]]"}
```

- 对 `file` 类型（图片）传 `file_type=file` 会报错：
  `file_type is optional, options: [doc,docx]`
- 因此 **无法通过 API 对图片文件新建评论或回复评论**
- 用户在飞书客户端（移动端/桌面端）**也无法对图片留言**（UI可能显示对话框但实际不存储）

## WebSocket 长连接脚本参考

```python
#!/usr/bin/env python3
"""Feishu WebSocket event listener - waits for comment notifications"""
import sys, json, os, time
from lark_oapi import EventDispatcherHandler, LogLevel
from lark_oapi.ws import Client as WSClient

APP_ID = "cli_a94f935cbd225ceb"
APP_SECRET = "msO20p...LaKi"

LOG_FILE = "/tmp/feishu_events.log"

def log_msg(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def handle_comment_add(event):
    event_data = event.event if hasattr(event, 'event') else {}
    event_type = event.header.event_type if hasattr(event, 'header') and event.header else 'unknown'
    event_id = event.header.event_id if hasattr(event, 'header') and event.header else 'unknown'
    log_msg(f"📬 收到事件! type={event_type}, id={event_id}")
    log_msg(f"数据: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
    # Create signal file
    signal_file = "/tmp/feishu_event_received.signal"
    with open(signal_file, "w") as f:
        json.dump({"event_type": event_type, "event_id": event_id,
                   "data": event_data, "timestamp": time.time()}, f, ensure_ascii=False)

def main():
    log_msg("🎯 启动飞书长连接监听器...")
    handler = EventDispatcherHandler.builder("", "") \
        .register_p2_customized_event("drive.notice.comment_add_v1", handle_comment_add) \
        .build()
    ws_client = WSClient(
        app_id=APP_ID, app_secret=APP_SECRET,
        event_handler=handler, log_level=LogLevel.ERROR,
        auto_reconnect=True
    )
    log_msg("✅ 连接中...")
    ws_client.start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_msg(f"❌ 错误: {e}")
        import traceback
        log_msg(traceback.format_exc())
```

**实测结论**：连接成功（输出 `connected to wss://msg-frontier.feishu.cn/ws/v2`），但用户留言后零事件到达。

## 关键决策历史
| 日期 | 决策 | 原因 |
|------|------|------|
| 2026-05-06 | ❌ 放弃轮询 | 用户明确不想用扫描方案 |
| 2026-05-06 | ❌ 放弃 WebSocket 长连接 | 连接成功但 `drive.notice.comment_add_v1` 事件不为图片触发 |
| 2026-05-06 | ❌ 整体方案放弃 | 飞书图片文件不支持评论，任何路径都不可行 |
| 2026-05-06 | ✅ 改用飞书 DM 沟通 | 用户在私聊中直接说"想你了"触发生图，简单可靠 |
