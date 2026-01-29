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

# 复制后端代码
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# ==================== Frontend Build Stage ====================
FROM node:20-slim as frontend-builder

WORKDIR /app

# 复制前端代码
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

# ==================== Runtime Stage ====================
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /app /app

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/dist ./frontend/dist

# 创建必要目录
RUN mkdir -p generated_projects/static/avatars \
    generated_projects/static/projects \
    data/chroma_db

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
