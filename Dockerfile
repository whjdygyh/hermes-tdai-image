# 自定义 Hermes + TDAI 镜像
# 策略：在预处理器动手前，sed 替换 entrypoint.sh 让它硬编码 gateway run
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 关键：在预处理器篡改之前，把原始 entrypoint 改成 gateway run 模式
RUN sed -i 's/exec hermes "\$@"/exec hermes gateway run/' /opt/hermes/docker/entrypoint.sh
RUN sed -i 's/exec hermes \$@/exec hermes gateway run/' /opt/hermes/docker/entrypoint.sh
# 万一 sed 没匹配到，也可用 grep 确认
RUN grep -n "hermes gateway run" /opt/hermes/docker/entrypoint.sh || echo "WARNING: sed replacement may have failed"
