# 自定义 Hermes + TDAI 镜像
# CACHE_BUSTER=20260529_001
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 备份原始 entrypoint
RUN cp /opt/hermes/docker/entrypoint.sh /opt/hermes/docker/entrypoint.sh.orig

# 用 heredoc 创建包装器脚本，然后覆盖 ENTRYPOINT（不动 COPY）
RUN cat > /opt/hermes/docker/entrypoint-wrapper.sh << 'WRAPPER'
#!/bin/bash
set +e
echo "=== [wrapper] Starting ==="
echo "=== [wrapper] Args: $@ ==="

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
echo "=== [wrapper] Handing off to original entrypoint ==="
exec /opt/hermes/docker/entrypoint.sh.orig "$@"
WRAPPER
RUN chmod +x /opt/hermes/docker/entrypoint-wrapper.sh

# 设置包装器为 ENTRYPOINT，确保 gateway 模式
ENTRYPOINT ["/opt/hermes/docker/entrypoint-wrapper.sh"]
CMD ["hermes", "gateway", "run"]
