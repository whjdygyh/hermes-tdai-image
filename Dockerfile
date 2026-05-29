# 自定义 Hermes + TDAI 镜像
# 最终策略：sed 嵌入 Node.js 安装步骤（预处理器无法丢弃基础依赖安装）
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22 + 修改 main-wrapper.sh 默认启动模式
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    sed -i 's/exec s6-setuidgid hermes hermes$/exec s6-setuidgid hermes hermes gateway run/' /opt/hermes/docker/main-wrapper.sh && \
    echo "main-wrapper gateway patch: $(grep -c 'gateway run' /opt/hermes/docker/main-wrapper.sh) occurrences"

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"
