# 自定义 Hermes + TDAI 镜像
# 策略：不用 heredoc/printf/COPY，用最原始的 echo+head+tail 防 zbpack 预处理
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

# 用 echo 逐行创建 TDAI 启动脚本
RUN echo "#!/bin/bash" > /opt/hermes/bin/tdai-start.sh
RUN echo "echo '=== [TDAI] Starting gateway ==='" >> /opt/hermes/bin/tdai-start.sh
RUN echo "echo '=== [TDAI] Args received: ' \$@" >> /opt/hermes/bin/tdai-start.sh
RUN echo "if ! curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  echo '=== [TDAI] Launching server ==='" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  mkdir -p /opt/data" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  cd /opt/data" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts &" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  sleep 4" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  if curl -sf http://127.0.0.1:8420/health >/dev/null 2>&1; then" >> /opt/hermes/bin/tdai-start.sh
RUN echo "    echo '=== [TDAI] Gateway OK ==='" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  else" >> /opt/hermes/bin/tdai-start.sh
RUN echo "    echo '=== [TDAI] WARNING: health check failed ==='" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  fi" >> /opt/hermes/bin/tdai-start.sh
RUN echo "else" >> /opt/hermes/bin/tdai-start.sh
RUN echo "  echo '=== [TDAI] Already running ==='" >> /opt/hermes/bin/tdai-start.sh
RUN echo "fi" >> /opt/hermes/bin/tdai-start.sh
RUN chmod +x /opt/hermes/bin/tdai-start.sh

# 用 head+tail 重建 entrypoint.sh，在 shebang 后插入 TDAI 启动
RUN echo "#!/bin/bash" > /opt/hermes/docker/entrypoint.sh
RUN echo "source /opt/hermes/bin/tdai-start.sh" >> /opt/hermes/docker/entrypoint.sh
RUN echo "" >> /opt/hermes/docker/entrypoint.sh
RUN tail -n +2 /opt/hermes/docker/entrypoint.sh.orig >> /opt/hermes/docker/entrypoint.sh
RUN chmod +x /opt/hermes/docker/entrypoint.sh

CMD ["hermes", "gateway", "run"]
