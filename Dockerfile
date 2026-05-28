# 自定义 Hermes + TDAI 镜像
# 基于 Hermes 官方镜像，增加 TDAI 记忆网关
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22（系统自带 Node 太旧，TDAI 需要 Node 22+）
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version

# 安装 TDAI 记忆网关
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件到插件目录
RUN cp -r /usr/local/lib/node_modules/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb /opt/hermes/plugins/memory/ 2>/dev/null; echo "Plugin installed"

# 安装启动脚本：先启动 TDAI 网关，再执行原始 entrypoint
COPY start.sh /opt/hermes/docker/start.sh
RUN chmod +x /opt/hermes/docker/start.sh

# 保留原始 entrypoint 不动，用启动脚本作为入口
ENTRYPOINT ["/opt/hermes/docker/start.sh"]
