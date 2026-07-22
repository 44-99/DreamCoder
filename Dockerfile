# DreamCoder Dockerfile
# 多阶段构建用于优化镜像大小

# ==================== Backend Build Stage ====================
FROM python:3.11-slim as backend-builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install the hosted-deployment adapters in the image.
COPY backend/requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-optional.txt

COPY backend/ .

# ==================== Runtime Stage ====================
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packages and console scripts such as uvicorn.
COPY --from=backend-builder /usr/local /usr/local
COPY --from=backend-builder /app /app

# 创建必要目录
RUN mkdir -p static/avatars \
    static/projects \
    data/chroma_db

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
