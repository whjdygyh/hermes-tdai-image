# 自定义 Hermes + TDAI 镜像
# 基于 Hermes 官方镜像，增加 TDAI 记忆网关

ARG HERMES_IMAGE=ghcr.io/hermes-agent/hermes:latest

FROM ${HERMES_IMAGE}

# 安装 Node.js 22（系统自带的 Node 太旧）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 TDAI 记忆网关依赖
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 修改 entrypoint：启动 TDAI 网关后再启动 Hermes
RUN sed -i 's|^exec hermes "\$@"|# Auto-start TDAI memory gateway\nif ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>\&1; then\n  echo "=== Starting TDAI gateway ==="\n  cd /opt/data\n  setsid npx tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai-gw.log 2>\&1 \&\n  sleep 4\n  echo "=== TDAI gateway started ==="\nfi\nexec hermes "\$@"|' /opt/hermes/docker/entrypoint.sh

# 复制 TDAI Hermes 插件到默认插件目录
RUN if [ -d "/usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb" ]; then \
      cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/; \
    fi
