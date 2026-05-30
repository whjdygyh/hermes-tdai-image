# 📸 相册 HTTP Server（本地访问 + 机器人API）

## 概述

将 Windows 相册路径 `C:\Users\Administrator\Documents\abots\lover_portraits\` 转为 HTTP 访问，
供机器人/其他程序通过 `http://localhost:8580/` 而非 `file://` 路径访问。

## 架构

```
Python http.server (WSL)
  ├── port 8580
  ├── 服务目录: /mnt/c/Users/Administrator/Documents/abots/lover_portraits/
  ├── CORS 跨域支持（* 允许所有来源）
  └── 自定义路由:
      ├── /            → 首页（目录导航 + 机器人用法说明）
      ├── /photos/     → 照片文件目录（直接访问原图）
      ├── /thumbs/     → 缩略图目录
      └── /api/list    → JSON 格式照片列表（供机器人用）
```

## 文件位置

| 文件 | 路径 |
|------|------|
| Python 服务器脚本 | `~/Alexander/photo_server.py` |
| 启停管理脚本 | `~/Alexander/photo_server.sh` |
| systemd 用户服务 | `~/.config/systemd/user/photo-server.service` |

## API 接口

### `GET /api/list` — 照片列表（JSON）

```json
{
  "total": 52,
  "photos": [
    { "name": "01_evening_sofa.jpg", "url": "/photos/01_evening_sofa.jpg", "path": "photos/01_evening_sofa.jpg" },
    { "name": "02_legs_sofa.jpg", "url": "/photos/02_legs_sofa.jpg", "path": "photos/02_legs_sofa.jpg" },
    ...
  ],
  "base_url": "http://localhost:8580"
}
```

### `GET /photos/<filename>` — 单张照片

```
curl http://localhost:8580/photos/51_ref04_driver_seat.jpg
```

## 启动/停止/状态

```bash
# systemd 服务（推荐 — 开机自启）
systemctl --user start photo-server
systemctl --user stop photo-server
systemctl --user status photo-server

# 管理脚本
bash ~/Alexander/photo_server.sh start
bash ~/Alexander/photo_server.sh stop
bash ~/Alexander/photo_server.sh status
```

## 开机自启（已配置）

- **systemd 用户服务**：`photo-server.service`
- **linger 已启用**：`sudo loginctl enable-linger admin1`（登出后服务继续运行）
- **自动重启**：`Restart=on-failure` + `RestartSec=5`
- 每次 WSL 启动后自动运行，无需手动操作

## 关键踩坑记录

### 1. `allow_reuse_address` 必须在实例化前设置

```python
# ❌ 错误：设置太晚
httpd = socketserver.TCPServer(("0.0.0.0", PORT), PhotoHandler)
httpd.allow_reuse_address = True  # 太晚了！bind() 已经执行过

# ✅ 正确：设置为类属性
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("0.0.0.0", PORT), PhotoHandler)
```

### 2. 端口清理

当 systemd 重启过快时，旧进程可能仍占用端口：

```bash
fuser -k 8580/tcp    # 强制杀掉占用进程
sleep 2              # 等待端口释放
systemctl --user restart photo-server
```

### 3. systemd ExecStart 要用完整 Python 路径

```ini
# ❌ 错误：`/usr/bin/python3` — 可能指向 Python 3.10，没有 Pillow
ExecStart=/usr/bin/python3 photo_server.py

# ✅ 正确：使用 Hermes venv 的 Python 3.11（包含 Pillow）
ExecStart=/home/admin1/.hermes/hermes-agent/venv/bin/python3 /path/to/photo_server.py
```

## 端口参考

| 服务 | 端口 |
|------|------|
| 相册 HTTP Server | **8580** |
| V2Ray SOCKS5 代理 | 10808 |

## 完整 Python 服务器脚本关键要素

```python
import http.server
import socketserver
import json

PORT = 8580
PHOTOS_DIR = "/mnt/c/Users/Administrator/Documents/abots/lover_portraits"
os.chdir(PHOTOS_DIR)

class PhotoHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == '/api/list':
            # 返回 JSON 照片列表
            ...
            return
        if self.path == '/':
            # 返回 HTML 首页
            ...
            return
        return super().do_GET()

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("0.0.0.0", PORT), PhotoHandler)
httpd.serve_forever()
```

## 机器人程序用法

```python
import requests

# 获取照片列表
r = requests.get("http://localhost:8580/api/list")
data = r.json()
print(f"共有 {data['total']} 张照片")

# 遍历所有照片
for photo in data['photos']:
    img_url = f"http://localhost:8580{photo['url']}"
    print(f"照片: {photo['name']} → {img_url}")
```
