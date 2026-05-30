#!/bin/bash
# Zeabur 兼容启动脚本 — 绕过 s6-overlay，直接启动 Hermes + TDAI
set +e

echo "=== [zeabur-entry] Starting Hermes + TDAI ==="

# 1. 启动 TDAI 记忆网关（后台）
if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
  echo "=== [zeabur-entry] Starting TDAI gateway ==="
  mkdir -p /opt/data
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
echo "=== [zeabur-entry] Starting Hermes gateway ==="
cd /opt/hermes
exec /opt/hermes/bin/hermes gateway run "$@"
