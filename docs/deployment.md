# DreamCoder 托管部署指南

本页描述当前仓库能够验证的部署形态。第一次使用请先完成[本地入门指南](./getting-started.md)；Docker、PostgreSQL 与 Redis 只解决托管场景的问题。

## 选择运行形态

| 场景 | 数据库 | 验证码状态 | 启动方式 |
|---|---|---|---|
| 个人学习、单进程开发 | SQLite | 进程内 TTL store | Python + Node.js |
| 团队测试环境 | PostgreSQL | Redis | Docker Compose `dev` profile |
| 单机公开部署 | PostgreSQL | Redis | 后端容器 + 构建后的前端 + Nginx/其他反向代理 |

当前版本没有 Kubernetes 清单、自动 TLS、正式数据库迁移或经过安全评审的多租户沙箱。不要把这些能力当作已支持。

## Docker Compose 开发环境

要求 Docker Engine 与 Compose v2：

```bash
docker --version
docker compose version
```

在仓库根目录创建 Compose 使用的 `.env`：

macOS / Linux：

```bash
cp backend/.env.example .env
```

Windows PowerShell：

```powershell
Copy-Item backend/.env.example .env
```

编辑根目录 `.env`，至少设置：

```env
ENVIRONMENT=development
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-key
SECRET_KEY=replace-with-a-long-random-value
AUTH_DELIVERY_MODE=console
```

启动 PostgreSQL、Redis、后端和 Vite 开发前端：

```bash
docker compose --profile dev up --build
```

检查：

- 前端：<http://localhost:5173>
- 后端：<http://localhost:8000/>
- OpenAPI：<http://localhost:8000/docs>

停止服务但保留数据库卷：

```bash
docker compose --profile dev down
```

删除命名卷会永久删除 PostgreSQL 与 Redis 数据，因此本指南不把 `down -v` 作为常规命令。

## 构建后的前端与 Nginx

生产 profile 中的 Nginx 挂载宿主机 `frontend/dist`，所以需要先构建：

macOS / Linux：

```bash
cd frontend
VITE_API_BASE_URL=/api npm run build
cd ..
docker compose --profile production up --build -d
```

Windows PowerShell：

```powershell
cd frontend
$env:VITE_API_BASE_URL="/api"
npm run build
cd ..
docker compose --profile production up --build -d
```

当前 `nginx.conf` 把 `/api/` 代理到后端，并把 `/static/` 代理到生成产物目录。部署到真实域名时，还需要在外层负载均衡器或 Nginx 中配置 HTTPS、真实域名与安全响应头。

## 公开部署的最低配置

```env
ENVIRONMENT=production
AUTH_DELIVERY_MODE=external
SECRET_KEY=high-entropy-secret-from-your-secret-manager
CORS_ALLOWED_ORIGINS=https://dreamcoder.example.com
REDIS_ENABLED=true
REDIS_REQUIRED=true
```

并配置以下一种验证码渠道：

- SMTP：`SMTP_SERVER`、`SMTP_PORT`、`SMTP_SENDER`、`SMTP_PASSWORD`
- 阿里云短信：`ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`、签名和模板变量

此外必须：

1. 不向公网暴露 PostgreSQL 的 `5432` 与 Redis 的 `6379`；
2. 将默认数据库密码替换为 secret，并限制网络；
3. 用 `CORS_ALLOWED_ORIGINS` 将 CORS 限制到真实前端 origin；
4. 在反向代理终止 HTTPS；
5. 备份 PostgreSQL 和生成项目目录；
6. 阅读[安全边界](./security.md)，不要把同源预览当作多租户沙箱。

仓库的 Compose 文件保留了便于本地调试的端口与默认值，不能原样视为生产加固方案。

## 不使用 Docker 的托管方式

安装托管 adapter：

```bash
cd backend
pip install -r requirements-optional.txt
```

设置外部服务：

```env
DATABASE_URL=postgresql://user:password@db-host:5432/dreamcoder
REDIS_ENABLED=true
REDIS_REQUIRED=true
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_DB=0
```

然后由 systemd、进程管理器或平台服务运行：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

前端执行 `npm run build` 后可由任意静态主机提供，但 `VITE_API_BASE_URL` 必须在构建时指向后端公开地址或反向代理路径。

## 运维检查

```bash
docker compose ps
docker compose logs --tail 200 backend
curl http://localhost:8000/
```

需要观察：

- 后端健康检查是否持续成功；
- provider 的限流、超时和无效模型错误；
- PostgreSQL 磁盘与备份恢复结果；
- Redis 不可用是否按 `REDIS_REQUIRED` 预期失败；
- 生成项目目录的容量增长。

## 数据库演进

当前应用启动时使用 SQLAlchemy `create_all` 创建缺失表，不会执行正式 schema migration。长期运行的托管实例在升级涉及模型结构的版本前，应先备份数据库并审阅差异。项目计划在 schema 继续演进前引入 Alembic。
