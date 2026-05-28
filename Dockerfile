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

# 备份原始 entrypoint（wrapper 需要它）
RUN cp /opt/hermes/docker/entrypoint.sh /opt/hermes/docker/entrypoint.sh.orig

# 安装 TDAI 启动包装器作为新的 ENTRYPOINT
# 先启动 TDAI（后台），然后 exec 交给原始 entrypoint
COPY entrypoint-wrapper.sh /opt/hermes/docker/entrypoint-wrapper.sh
RUN chmod +x /opt/hermes/docker/entrypoint-wrapper.sh

ENTRYPOINT ["/opt/hermes/docker/entrypoint-wrapper.sh"]
CMD ["hermes", "gateway", "run"]
