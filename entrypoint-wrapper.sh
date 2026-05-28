#!/bin/bash
# Hermes + TDAI 启动包装器 v2 - 带详细调试日志
set +e

echo "=== [wrapper] Starting ==="
echo "=== [wrapper] Args: $0 $@ ==="
echo "=== [wrapper] User: $(id -u) ($(id -un)) ==="
echo "=== [wrapper] PWD: $(pwd) ==="

# Start TDAI
if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
  echo "=== [wrapper] Starting TDAI gateway ==="
  mkdir -p /opt/data
  cd /opt/data
  tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts &
  sleep 4
  if curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then
    echo "=== [wrapper] TDAI gateway started ==="
  else
    echo "=== [wrapper] WARNING: TDAI may not have started ==="
  fi
else
  echo "=== [wrapper] TDAI already running ==="
fi

# Check if original entrypoint exists
if [ -f /opt/hermes/docker/entrypoint.sh.orig ]; then
  echo "=== [wrapper] entrypoint.sh.orig exists ==="
  head -3 /opt/hermes/docker/entrypoint.sh.orig
else
  echo "=== [wrapper] ERROR: entrypoint.sh.orig NOT FOUND! ==="
  ls -la /opt/hermes/docker/entrypoint.sh*
  echo "=== [wrapper] Sleeping to keep container alive for debugging ==="
  sleep 3600
  exit 1
fi

# Check if hermes command is available
echo "=== [wrapper] Checking hermes availability ==="
if command -v hermes >/dev/null 2>&1; then
  echo "=== [wrapper] hermes found at: $(which hermes) ==="
else
  echo "=== [wrapper] hermes NOT on PATH ==="
  # Try to find it
  find /opt/hermes -name "hermes" -type f 2>/dev/null | head -5
  echo "=== [wrapper] PATH=$PATH ==="
fi

echo "=== [wrapper] Handing off to original entrypoint ==="
echo "=== [wrapper] exec /opt/hermes/docker/entrypoint.sh.orig $@ ==="

set -e
exec /opt/hermes/docker/entrypoint.sh.orig "$@"

# Should never reach here
echo "=== [wrapper] ERROR: exec failed! Sleeping to debug ==="
sleep 3600
exit 1
