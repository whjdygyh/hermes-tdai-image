#!/bin/bash
set -e

# Auto-start TDAI memory gateway
if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
  echo "=== Starting TDAI gateway ==="
  cd /opt/data
  npx --yes tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai-gw.log 2>&1 &
  sleep 4
  echo "=== TDAI gateway started ==="
fi

# Hand off to Hermes original entrypoint
exec /opt/hermes/docker/entrypoint.sh "$@"
