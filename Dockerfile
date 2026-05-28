# 自定义 Hermes + TDAI 镜像
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version

# 安装 TDAI 记忆网关（全局安装 tsx 就不用 npx 绕了）
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 在 entrypoint.sh 前面嵌入 TDAI 自启动逻辑，不动 ENTRYPOINT
# 关键改进：TDAI 启动失败不应阻止 Hermes 主进程
RUN cp /opt/hermes/docker/entrypoint.sh /opt/hermes/docker/entrypoint.sh.orig && \
    printf '%s\n' \
      '#!/bin/bash' \
      'set -e' \
      '' \
      '# ===== Auto-start TDAI memory gateway =====' \
      '# TDAI 启动失败不阻断 Hermes 主进程' \
      'set +e' \
      'if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then' \
      '  echo "=== Starting TDAI gateway ==="' \
      '  mkdir -p /opt/data' \
      '  cd /opt/data' \
      '  tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai.log 2>&1 &' \
      '  sleep 4' \
      '  if curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then' \
      '    echo "=== TDAI gateway started successfully ==="' \
      '  else' \
      '    echo "=== WARNING: TDAI gateway may not have started - check /tmp/tdai.log ==="' \
      '  fi' \
      'fi' \
      'set -e' \
      '' \
      '# ===== Original entrypoint =====' \
      > /opt/hermes/docker/entrypoint.sh && \
    cat /opt/hermes/docker/entrypoint.sh.orig >> /opt/hermes/docker/entrypoint.sh && \
    chmod +x /opt/hermes/docker/entrypoint.sh
