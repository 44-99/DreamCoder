# DreamCoder hosted deployment

This page documents deployment shapes the repository can currently support. Complete the [local quickstart](./getting-started.en.md) first. Docker, PostgreSQL, and Redis solve hosted-environment needs; they are not first-use requirements.

## Choose a runtime profile

| Scenario | Database | Verification state | Startup |
|---|---|---|---|
| Individual learning, single process | SQLite | In-process TTL store | Python + Node.js |
| Team test environment | PostgreSQL | Redis | Docker Compose `dev` profile |
| Single-host public deployment | PostgreSQL | Redis | Backend container + built frontend + Nginx or another proxy |

The current release does not include Kubernetes manifests, automatic TLS, formal database migrations, or a security-reviewed multi-tenant sandbox. Do not present those as supported capabilities.

## Docker Compose development environment

Check Docker Engine and Compose v2:

```bash
docker --version
docker compose version
```

Create the root `.env` used by Compose.

macOS / Linux:

```bash
cp backend/.env.example .env
```

Windows PowerShell:

```powershell
Copy-Item backend/.env.example .env
```

At minimum, set:

```env
ENVIRONMENT=development
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-key
SECRET_KEY=replace-with-a-long-random-value
AUTH_DELIVERY_MODE=console
```

Start PostgreSQL, Redis, the backend, and the Vite development frontend:

```bash
docker compose --profile dev up --build
```

Check:

- frontend: <http://localhost:5173>
- backend: <http://localhost:8000/>
- OpenAPI: <http://localhost:8000/docs>

Stop services while preserving named data volumes:

```bash
docker compose --profile dev down
```

Removing named volumes permanently deletes PostgreSQL and Redis data, so this guide does not present `down -v` as a routine command.

## Built frontend and Nginx

The production-profile Nginx mounts `frontend/dist` from the host, so build it first.

macOS / Linux:

```bash
cd frontend
VITE_API_BASE_URL=/api npm run build
cd ..
docker compose --profile production up --build -d
```

Windows PowerShell:

```powershell
cd frontend
$env:VITE_API_BASE_URL="/api"
npm run build
cd ..
docker compose --profile production up --build -d
```

The current `nginx.conf` proxies `/api/` to the backend and `/static/` to generated artifacts. A real domain still needs HTTPS termination, its actual server name, and security headers at this or an outer proxy.

## Minimum public-hosting configuration

```env
ENVIRONMENT=production
AUTH_DELIVERY_MODE=external
SECRET_KEY=high-entropy-secret-from-your-secret-manager
CORS_ALLOWED_ORIGINS=https://dreamcoder.example.com
REDIS_ENABLED=true
REDIS_REQUIRED=true
```

Configure one verification channel:

- SMTP: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_SENDER`, `SMTP_PASSWORD`
- Alibaba Cloud SMS: access key, secret, sign name, and template variables

You must also:

1. keep PostgreSQL `5432` and Redis `6379` off the public internet;
2. replace default database credentials and restrict the network;
3. restrict CORS to the real frontend origin with `CORS_ALLOWED_ORIGINS`;
4. terminate HTTPS at the reverse proxy;
5. back up PostgreSQL and the generated-project directory;
6. read [Security boundaries](./security.en.md) and do not treat same-origin preview as a multi-tenant sandbox.

The repository Compose file retains ports and defaults convenient for local debugging. It is not a production-hardening recipe as-is.

## Hosted deployment without Docker

Install the hosted adapters:

```bash
cd backend
pip install -r requirements-optional.txt
```

Configure external services:

```env
DATABASE_URL=postgresql://user:password@db-host:5432/dreamcoder
REDIS_ENABLED=true
REDIS_REQUIRED=true
REDIS_HOST=redis-host
REDIS_PORT=6379
REDIS_DB=0
```

Run the backend under systemd, a process manager, or your hosting platform:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Any static host can serve the result of `npm run build`, but `VITE_API_BASE_URL` must point to the public backend address or reverse-proxy path at build time.

## Operational checks

```bash
docker compose ps
docker compose logs --tail 200 backend
curl http://localhost:8000/
```

Monitor:

- continuous backend health-check success;
- provider rate-limit, timeout, and invalid-model errors;
- PostgreSQL disk use and restore tests;
- whether Redis failure follows the configured `REDIS_REQUIRED` behavior;
- generated-project storage growth.

## Database evolution

Application startup currently uses SQLAlchemy `create_all` to create missing tables; it does not perform formal schema migrations. Back up long-running hosted databases and review model changes before upgrading. The roadmap adds Alembic before further schema evolution.
