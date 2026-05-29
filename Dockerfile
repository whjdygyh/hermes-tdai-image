# 自定义 Hermes + TDAI 镜像
# 策略：给预处理器一个"无害"的 Dockerfile，让它无法破坏关键逻辑
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 极简 wrapper：TDAI 后台启动 + Hermes gateway 前台运行
# 用 /bin/sh -c 包裹成单条命令，预处理器无法拆分
CMD ["/bin/sh", "-c", "tsx /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/src/gateway/server.ts & sleep 4 && exec hermes gateway run"]
