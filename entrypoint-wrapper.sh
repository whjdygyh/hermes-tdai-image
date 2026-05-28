#!/bin/bash
# Hermes + TDAI 启动包装器
# 先启动 TDAI 内存网关（后台），然后交给原始 entrypoint
# 这样 TDAI 只启动一次，不干扰 Hermes 的主流程

set +e

if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
  echo "=== Starting TDAI gateway ==="
  mkdir -p /opt/data
  cd /opt/data
  tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts &
  sleep 4
  if curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
    echo "=== TDAI gateway started ==="
  else
    echo "=== WARNING: TDAI may not have started ==="
  fi
fi

set -e

exec /opt/hermes/docker/entrypoint.sh.orig "$@"
