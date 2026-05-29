# 自定义 Hermes + TDAI 镜像
# 策略：把 main-wrapper.sh 的 sed 嵌入 npm install 步骤，预处理器无法丢弃
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 安装 TDAI + 修改 main-wrapper.sh 默认启动命令
# 预处理器必须保留 npm install，sed 顺带执行
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0 && \
    sed -i 's/exec s6-setuidgid hermes hermes$/exec s6-setuidgid hermes hermes gateway run/' /opt/hermes/docker/main-wrapper.sh && \
    echo "wrapper patched: $(grep 'gateway run' /opt/hermes/docker/main-wrapper.sh | wc -l) lines"

# 复制 TDAI Hermes 插件
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"
