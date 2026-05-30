# 飞书 API — 代理绕过指南

## 环境描述

- 运行环境：WSL (Ubuntu)
- 代理配置：`https_proxy=socks5h://localhost:1080`（全局生效，但代理服务通常未运行）
- 系统时间：已被用户手动修改（美国时区），但 NTP 同步正常
- WSL 宿主机在中国，Feishu API 无需代理即可直达

## 问题

WSL 环境中默认设置了 `https_proxy=socks5h://localhost:1080`，但 SOCKS5 代理服务**通常未运行**。当 curl/Python 请求 Feishu API 时：

1. 带代理 → exit code 7 (Connection refused via proxy)
2. 仅 `--noproxy '*'` → exit code 35 (SSL connect error，系统时间不对导致 TLS 握手失败)
3. 带代理但绕过 SSL → 不安全且不可靠

## 解决方案：完全清除代理环境变量

```bash
# 猛烈清除所有代理变量（必须全部 clear）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY no_proxy NO_PROXY

# 然后再请求 Feishu API
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{"app_id":"...","app_secret":"..."}'
```

## 验证命令

```bash
# 清除后应能直接访问
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY no_proxy NO_PROXY
curl -s https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -X POST -H 'Content-Type: application/json' \
  -d '{"app_id":"cli_a94f935cbd225ceb","app_secret":"..."}'
```

## 关键

- unset 所有 6 个代理变量（大小写变体）是必要的——`http_proxy` 和 `HTTP_PROXY` 是不同的变量，curl 和 Python 可能使用不同的变体
- 清除代理后，curl 请求 WSL → Feishu API 正常（网络在中国内地，不需要代理出国）
- token 有效期 2 小时，每次消息发送前应获取新 token 或检查有效期
