# Hermes + TDAI 镜像 (Zeabur 兼容版)
# 绕过 s6-overlay，用自定义 entrypoint 直接启动 hermes + TDAI
FROM docker.io/nousresearch/hermes-agent:v2026.4.30

# 安装 Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    node --version

# 安装 TDAI 记忆网关 + tsx
RUN npm install -g @tencentdb-agent-memory/memory-tencentdb@0.3.5 tsx@4.22.0

# 复制 TDAI Hermes 插件
RUN NPM_ROOT=$(npm root -g); \
    cp -r "$NPM_ROOT/@tencentdb-agent-memory/memory-tencentdb/hermes-plugin/memory/memory_tencentdb" /opt/hermes/plugins/memory/ 2>/dev/null; \
    echo "TDAI plugin installed"

# 复制 Zeabur 兼容启动脚本（不依赖 s6-overlay）
COPY entrypoint-zeabur.sh /entrypoint-zeabur.sh
RUN chmod +x /entrypoint-zeabur.sh

ENTRYPOINT ["/entrypoint-zeabur.sh"]
CMD ["--profile", "lover"]
