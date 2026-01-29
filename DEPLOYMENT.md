# DreamCoder 部署指南

## 环境准备

### 1. 安装Docker和Docker Compose
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 配置环境变量
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置：
```env
# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dreamcoder?client_encoding=utf8

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OpenAI配置（必需）
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LangSmith配置（可选，用于调试）
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=dreamcoder-game-generation

# 阿里云配置（可选，用于验证码）
ALIBABA_CLOUD_ACCESS_KEY_ID=
ALIBABA_CLOUD_ACCESS_KEY_SECRET=
```

## 本地开发部署

### 方式一：使用Docker Compose（推荐）

1. **启动基础服务**
```bash
docker-compose up postgres redis -d
```

2. **启动后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **启动前端**
```bash
cd frontend
npm install
npm run dev
```

访问：
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 方式二：本地安装依赖

1. **PostgreSQL**
```bash
# Ubuntu
sudo apt-get install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres psql
CREATE DATABASE dreamcoder;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE dreamcoder TO postgres;
\q
```

2. **Redis**
```bash
# Ubuntu
sudo apt-get install redis-server

# 启动
sudo systemctl start redis
sudo systemctl enable redis
```

3. **Python环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Node.js环境**
```bash
cd frontend
npm install
```

## 生产环境部署

### 方式一：使用Docker Compose

1. **构建前端**
```bash
cd frontend
npm run build
```

2. **启动所有服务**
```bash
cd ..
docker-compose --profile production up -d
```

3. **查看日志**
```bash
docker-compose logs -f backend
docker-compose logs -f nginx
```

4. **停止服务**
```bash
docker-compose down
```

### 方式二：使用Docker Swarm/Kubernetes

对于大规模部署，建议使用Kubernetes。参考 `k8s/` 目录下的配置文件。

## 数据库迁移

首次运行需要创建数据库表：

```bash
cd backend
python -c "from main import Base, engine; Base.metadata.create_all(bind=engine); print('数据库表创建完成')"
```

## 监控和日志

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 健康检查
```bash
curl http://localhost:8000/
```

## 故障排查

### 问题1：后端无法连接数据库
```bash
# 检查PostgreSQL是否运行
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres

# 重启PostgreSQL
docker-compose restart postgres
```

### 问题2：前端无法连接后端
检查 `frontend/src/utils/axios.js` 中的API_BASE_URL配置。

### 问题3：OpenAI API调用失败
确保 `.env` 中 `OPENAI_API_KEY` 已正确配置。

### 问题4：端口冲突
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 将8000改为8001
```

## 性能优化

### 1. 启用Redis缓存
确保Redis正常运行，后端会自动使用Redis缓存验证码。

### 2. 数据库连接池
在 `backend/core/dependencies.py` 中调整连接池大小：
```python
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### 3. Nginx配置
生产环境建议启用gzip压缩和静态文件缓存（已在 `nginx.conf` 中配置）。

## 安全建议

1. **修改默认密钥**
   - 更改 `SECRET_KEY`
   - 使用强密码配置PostgreSQL和Redis

2. **启用HTTPS**
   - 配置SSL证书
   - 修改Nginx配置监听443端口

3. **防火墙配置**
   - 只开放必要端口（80, 443）
   - 限制数据库访问IP

4. **定期备份**
   - PostgreSQL数据备份
   - Redis持久化数据备份

## 更新和维护

### 更新代码
```bash
git pull origin main

# 重建前端
cd frontend
npm run build

# 重启服务
docker-compose --profile production up -d --force-recreate
```

### 数据备份
```bash
# PostgreSQL备份
docker-compose exec postgres pg_dump -U postgres dreamcoder > backup.sql

# 恢复
docker-compose exec -T postgres psql -U postgres dreamcoder < backup.sql
```

## 扩展阅读

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Docker文档](https://docs.docker.com/)
- [Vue 3文档](https://vuejs.org/)
- [LangChain文档](https://docs.langchain.com/)
