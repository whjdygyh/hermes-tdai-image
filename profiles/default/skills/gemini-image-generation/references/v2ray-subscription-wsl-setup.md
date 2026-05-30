# V2Ray 订阅配置 & WSL 直连代理搭建

> **场景**：Windows V2Ray 客户端路由规则未包含 `googleapis.com`，或节点不稳定，需要在 WSL 中搭建独立代理通道。

---

## 1. 获取订阅 / 配置信息

### 从 Feishu 二维码提取

当用户发送 V2Ray 配置的截图/二维码（Feishu 消息中的图片）时：

**已知限制**：
- WSL 环境缺少 zbar/opencv 库（`ImportError: No module named 'pyzbar'`，`No module named 'cv2'`）
- 安装这些库需要 libzbar0 系统包 + Python 绑定，可能需 root/sudo
- **替代方案**：直接让用户粘贴 `vmess://` / `vless://` / `ss://` 文本配置链接
- 也可以尝试用 `vision_analyze` 工具读 QR 码文字

### 配置格式

用户提供的配置通常有三种格式：

| 格式 | 示例 | 处理方式 |
|------|------|----------|
| `vmess://...` | base64 编码的 VMess 配置 | 解码后写入 config.json |
| `vless://...` | 明文 URI | 直接解析参数 |
| `ss://...` | Shadowsocks URI | 直接解析参数 |

---

## 2. 在 WSL 中安装 V2Ray 客户端

### 安装 v2ray-core 或 xray-core

```bash
# 方案A: 下载预编译二进制
V2RAY_VERSION="v5.26.0"
wget "https://github.com/v2fly/v2ray-core/releases/download/${V2RAY_VERSION}/v2ray-linux-64.zip"
unzip v2ray-linux-64.zip -d ~/v2ray/
chmod +x ~/v2ray/v2ray ~/v2ray/v2ctl

# 方案B: 使用 xray（兼容 V2Ray 配置，更活跃）
curl -Ls https://github.com/XTLS/Xray-install/raw/main/install-release.sh | bash
```

### 从订阅链接生成配置

vmess:// 链接解码后通常包含以下字段，需转换为 V2Ray config.json：

- `inbounds`: SOCKS5 @ 127.0.0.1:10809 + HTTP @ 127.0.0.1:10810
- `outbounds`: protocol=vmess, 含 address/port/id/alterId 及 streamSettings (network/ws/tls)
- `routing`: domainStrategy=AsIs, 全部流量走 proxy outbound

### 启动命令

```bash
~/v2ray/v2ray run -c config.json &
```

### 验证

```bash
# 先测国内（确认端口活着）
curl -x socks5://127.0.0.1:10809 --connect-timeout 5 \
  -s -o /dev/null -w "%{http_code}" https://www.baidu.com
# 200 → 端口存活

# 再测 Google（验证能否出境）
curl -x socks5://127.0.0.1:10809 --connect-timeout 15 -s \
  "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | head -c 200
# 有 JSON 返回 → 成功！
```

---

## 3. 与 Windows V2Ray 客户端共存

| 特性 | Windows V2Ray (172.20.128.1:10808) | WSL V2Ray (127.0.0.1:10809) |
|------|-----------------------------------|------------------------------|
| 路由规则 | 由 Windows 客户端控制 | 由我们完全控制 ⭐ |
| 代理质量 | 可能不包含 Google 域名 | force 全部出境 |
| 稳定性 | 依赖用户操作 | 独立进程，可后台保持 |
| 端口冲突 | 无 | 无（不同端口） |

**推荐策略**：
1. 优先用 WSL V2Ray（完全控制路由规则，不依赖 Windows 客户端配置）
2. Windows V2Ray 作为备用（如果 WSL 的节点也挂了）

---

## 4. 常见问题

### 订阅链接无法解码

vmess:// 链接通常在 `#` 后有节点名，`vmess://` 后面是 base64(base64(JSON))：
```python
import base64, json
b64_str = "vmess_link_part_after_vmess://..."
try:
    decoded = base64.b64decode(b64_str)
    config = json.loads(decoded)
except:
    decoded = base64.b64decode(base64.b64decode(b64_str))
    config = json.loads(decoded)
```

### 编译错误 / 缺少库

```bash
# 安装 QR 解码工具（Python）
sudo apt-get install -y libzbar0
pip install pyzbar opencv-python-headless
```
