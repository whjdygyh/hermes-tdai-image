# 自定义 Hermes + TDAI 镜像
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

# 在 entrypoint.sh 前面加上 TDAI 自启动逻辑，不动 ENTRYPOINT
RUN cp /opt/hermes/docker/entrypoint.sh /opt/hermes/docker/entrypoint.sh.orig && \
    printf '%s\n' \
      '#!/bin/bash' \
      'set -e' \
      '' \
      '# ===== Auto-start TDAI memory gateway =====' \
      'if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then' \
      '  echo "=== Starting TDAI gateway ==="' \
      '  cd /opt/data' \
      '  npx --yes tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai.log 2>&1 &' \
      '  sleep 4' \
      '  echo "=== TDAI gateway started ==="' \
      'fi' \
      '' \
      '# ===== Original entrypoint =====' \
      > /opt/hermes/docker/entrypoint.sh && \
    cat /opt/hermes/docker/entrypoint.sh.orig >> /opt/hermes/docker/entrypoint.sh && \
    chmod +x /opt/hermes/docker/entrypoint.sh
