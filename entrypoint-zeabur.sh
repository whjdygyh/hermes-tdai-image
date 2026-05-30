#!/bin/bash
# Zeabur 兼容启动脚本 — 绕过 s6-overlay shim，直接启动 Hermes + TDAI
# 此脚本是容器的 ENTRYPOINT，CMD ("gateway", "run") 通过 $@ 传入
set +e

echo "=== [zeabur-entry] Starting Hermes + TDAI ==="

# Ensure /opt/data exists
mkdir -p /opt/data

# 1. 启动 TDAI 记忆网关（后台）
if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
  echo "=== [zeabur-entry] Starting TDAI gateway ==="
  cd /opt/data
  tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai.log 2>&1 &
  sleep 3
  if curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
    echo "=== [zeabur-entry] TDAI OK ==="
  else
    echo "=== [zeabur-entry] TDAI may not be ready, continuing anyway ==="
  fi
else
  echo "=== [zeabur-entry] TDAI already running ==="
fi

# 2. 启动 Hermes Gateway（前台，作为主进程）
# 使用 venv 二进制绕过 s6 shim（s6-setuidgid 在 Prebuilt Image 模式下不可用）
echo "=== [zeabur-entry] Starting Hermes gateway ==="
export HOME=/opt/data
exec /opt/hermes/.venv/bin/hermes "$@"
