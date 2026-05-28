# 自定义 Hermes + TDAI 镜像
# 基于 Hermes 官方镜像，增加 TDAI 记忆网关
# 构建: docker build -t yourname/hermes-tdai .
# 使用: docker pull yourname/hermes-tdai

FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22（系统自带 Node 太旧，TDAI 需要 Node 22+）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 修改 entrypoint：启动 TDAI 网关后再启动 Hermes
RUN sed -i 's|^exec hermes "\$@"|# Auto-start TDAI memory gateway\nif ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then\n  echo "=== Starting TDAI gateway ==="\n  cd /opt/data\n  setsid npx --yes tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts > /tmp/tdai-gw.log 2>&1 &\n  sleep 4\n  echo "=== TDAI gateway started ==="\nfi\nexec hermes "\$@"|' /opt/hermes/docker/entrypoint.sh

# 复制 TDAI Hermes 插件到插件目录
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"
