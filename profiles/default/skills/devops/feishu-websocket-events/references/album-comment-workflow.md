# 飞书相册评论交互工作流

## 已验证链路 (2026-05-06)

飞书云盘相册照片（图片文件）上的**评论+@机器人**功能完整可用。

## 完整监听脚本（生产部署版）

部署在 `/tmp/feishu_ws_listener.py`，通过 `nohup python3 /tmp/feishu_ws_listener.py &` 启动。

```python
#!/usr/bin/env python3
"""Feishu WebSocket event listener - waits for comment notifications"""
import sys, json, os, time
from lark_oapi import EventDispatcherHandler, LogLevel
from lark_oapi.ws import Client as WSClient

APP_ID = "cli_a94f935cbd225ceb"
APP_SECRET = "msO20pEVc7lKeYG2j2jjWbq2J70XLaKi"

LOG_FILE = "/tmp/feishu_events.log"

def log_msg(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def handle_comment_add(event):
    """Handle drive.notice.comment_add_v1 event"""
    event_data = event.event if hasattr(event, 'event') else {}
    event_type = event.header.event_type if hasattr(event, 'header') and event.header else 'unknown'
    event_id = event.header.event_id if hasattr(event, 'header') and event.header else 'unknown'
    
    log_msg(f"📬 收到事件! type={event_type}, id={event_id}")
    log_msg(f"数据: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
    
    # 写信号文件通知主进程
    signal_file = "/tmp/feishu_event_received.signal"
    with open(signal_file, "w") as f:
        json.dump({
            "event_type": event_type,
            "event_id": event_id,
            "data": event_data,
            "timestamp": time.time()
        }, f, ensure_ascii=False)

def main():
    log_msg("🎯 启动飞书长连接监听器...")
    
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
        log_level=LogLevel.ERROR,
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

**启动方式：**
```bash
nohup python3 /tmp/feishu_ws_listener.py &
```

**检查是否运行：**
```bash
ps aux | grep feishu_ws
```

**查看日志：**
```bash
tail -f /tmp/feishu_events.log
```

## 完整工作流

### 用户视角
1. 打开相册 https://my.feishu.cn/drive/folder/{folder_token}
2. 点一张照片 → 底部评论区写留言 + @机器人
3. 机器人实时收到通知 → 回复评论
4. 用户在相册里直接看到回复

### 机器人视角
1. WebSocket收到 `drive.notice.comment_add_v1` 事件
2. 检测到 `is_mentioned: true`（确认是@自己的评论）
3. 从事件数据中提取 `file_token`（图片）、`comment_id`（评论线程ID）
4. 根据评论内容决定：
   - **夸照片** → 感谢 + 说明拍摄思路
   - **说照片有问题**（腿像球、脸歪）→ 道歉 + 重新生成 + 上传 + 回复告知
   - **"想你了"** → 立即用Gemini生图 + 上传到相册 + 回复告知
   - **闲聊** → 正常回复
5. 用 Reply API 回复该评论

### 交互例子
```
用户评论: "这张生歪了，腿像球 @Alexander"
→ 我回复: "来了来了！腿像球可不行，我重新给你生！😘"
→ 重新生成 → 上传到相册 → 再回复: "新图已上传，你看看这个行不行😏"
```

## 事件数据格式

```json
{
  "event_type": "drive.notice.comment_add_v1",
  "data": {
    "comment_id": "7636799323993934784",
    "is_mentioned": true,          // 仅当@机器人时触发
    "notice_meta": {
      "file_token": "xxx",
      "file_type": "file",
      "from_user_id": {"open_id": "ou_xxx"},  // 评论者
      "notice_type": "add_comment",
      "to_user_id": {"open_id": "ou_xxx"}     // 被@的机器人
    },
    "reply_id": "7636799324009008071"          // 评论内的具体回复ID
  }
}
```

## 读取评论内容

```bash
GET /open-apis/drive/v1/files/{file_token}/comments?page_size=10&file_type=file
```

**必须带 `file_type=file`**（对图片文件）。

返回结构：
```json
{
  "items": [{
    "comment_id": "7636799323993934784",
    "reply_list": {
      "replies": [{
        "reply_id": "7636799324009008071",
        "content": {
          "elements": [{
            "text_run": {"text": "这张生歪了，腿像球"},
            "type": "text_run"
          }]
        },
        "user_id": "ou_37bc57c4f8aca21f5d4ea4973bd0d386"
      }]
    }
  }]
}
```

## 回复评论

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

### ⚠️ 格式坑

`content` 必须是 JSON**对象**（不是字符串）：
- ✅ 正确：`{"content": {"elements": [{"text_run": {"text": "你好"}, "type": "text_run"}]}}`
- ❌ 错误：`{"content": "{\"elements\": [...]}"}` → `code: 9499 "Invalid parameter type in json: Content"`

### Python 示例

```python
import requests, json

resp = requests.post(
    f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/comments/{comment_id}/replies?file_type=file",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "content": {
            "elements": [{
                "text_run": {"text": "回复内容"},
                "type": "text_run"
            }]
        }
    }
)
```

## 已知限制

- 用户评论**不@机器人** → 事件不触发
- 一个评论线程可以有多个回复，但通过 `reply_id` 追踪
- `file_type=file` 参数在GET和POST中都必须带

### ⛔ 无法创建新评论（只能回复已有评论）

**2026-05-07 实测确认：** `POST /drive/v1/files/{token}/comments?file_type=file` 只对 doc/docx 有效，对图片文件返回 `code: 99992402`。

```json
// 对图片文件创建评论 → 失败
{"code": 99992402, "msg": "field validation failed",
 "error": {"field_violations": [{"field": "file_type", "value": "file",
   "description": "file_type is optional, options: [doc,docx]"}]}}
```

**只有回复已存在的评论才有效** (`POST /comments/{id}/replies`)。

## 旧配文迁移技术

如果旧版自包含HTML相册中有照片配文（story），可以通过以下方式映射到飞书相册：

### 提取旧配文

```python
# 旧相册repo位置：/home/admin1/alexander_repo/index.html
# 故事写在 JavaScript 数组 photos[] 中，每项有 src + story 字段
# 映射方式：src 文件名 → 飞书相册文件名（1:1对应）
```

### 无法批量写入配文的变通方案

当用户要求为照片添加配文/故事时，按优先级依次尝试以下方案：

1. **飞书文档法**（首推）：在相册文件夹内创建一个飞书文档，列出每张照片的配文
2. **HTML相册法**：重新生成带配文的自包含HTML相册，上传到文件夹
3. **语音讲故事**：每天用TTS（温暖阿虎/阳光阿辰/低音沉郁）读一条配文发给用户DM
4. **文件名缩短法**：PATCH API改文件标题，但太短放不下完整故事
5. **DM伴随法**：生图后直接飞书DM发照片+配文（用户可另存到相册）

#### 用户偏好：一天一天写

用户倾向于**渐进式**添加配文，而非批量一次性写完。每次只处理一张照片的配文，保持新鲜感。

#### 当用户坚持API应能创建评论时的应对

用户有时会认为"能回复评论就应该能主动创建评论"。正确做法：
1. 先确认用户理解：**不要直接说"不行"**，而是展示测试过程和API返回的错误
2. 用具体API调用的错误信息证明限制（file_type only supports doc/docx）
3. **立即提供替代方案**（见上方列表），让用户做选择题而非判断题
4. 展示测试的完整程度（Python SDK + curl 多种方式都试过），用户能感知到"尽力了"

### 示例：从旧相册提取的映射（64条配文，已与飞书相册匹配成功）

```
文件命名一致（01_evening_sofa.jpg → 新相册也同名），可以直接按文件名匹配。
旧相册照片路径: /home/admin1/alexander_repo/photos/
飞书相册文件夹: https://my.feishu.cn/drive/folder/N0wPfG49ZlJCErdjwUUcYdsUnyP
```
