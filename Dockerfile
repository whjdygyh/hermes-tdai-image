# 自定义 Hermes + TDAI 镜像
# 策略：修改 main-wrapper.sh 默认启动命令为 gateway run，防 CMD 被 zbpack 丢弃
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 把 main-wrapper.sh 的无参数默认值从 "hermes" 改成 "hermes gateway run"
# 这样即使 zbpack 丢弃 CMD，容器也会以 gateway 模式启动
RUN sed -i 's/exec s6-setuidgid hermes hermes$/exec s6-setuidgid hermes hermes gateway run/' /opt/hermes/docker/main-wrapper.sh
RUN grep "gateway run" /opt/hermes/docker/main-wrapper.sh || echo "WARNING: sed may have failed"
