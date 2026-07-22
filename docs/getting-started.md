# DreamCoder 入门：十分钟生成第一个 Web 小游戏

本指南面向第一次运行 DreamCoder 的开发者。目标是先用最少依赖完成一次“描述 → 生成 → 预览”，再决定是否启用 Docker 或其他可选基础设施。

| 项目 | 要求 | 检查命令 |
|---|---|---|
| Git | 任意近期版本 | `git --version` |
| Python | 3.11+ | `python --version` |
| Node.js | 20.19+ 或 22.12+ | `node --version` |
| npm | 随 Node.js 安装 | `npm --version` |
| 模型凭据 | DeepSeek、OpenAI、Qwen 三选一 | 在 provider 控制台创建 |

Docker、PostgreSQL、Redis 和 ChromaDB 都不是本地启动前提。

## 1. 获取代码与环境文件

```bash
git clone https://github.com/44-99/DreamCoder.git
cd DreamCoder
```

macOS / Linux：

```bash
cp backend/.env.example backend/.env
```

Windows PowerShell：

```powershell
Copy-Item backend/.env.example backend/.env
```

## 2. 配置一个模型 provider

编辑 `backend/.env`。默认示例是 DeepSeek：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-key
```

也可以改为 OpenAI：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

或 Qwen：

```env
LLM_PROVIDER=qwen
QWEN_API_KEY=your-key
```

模型 ID、Base URL 和其他变量都在 [`backend/.env.example`](../backend/.env.example) 中。模型目录会变化；如果 provider 返回“模型不存在”，先到其官方目录核对并覆盖对应的 `*_MODEL`。

## 3. 启动后端

macOS / Linux：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

### 检查点：后端已工作

打开 <http://localhost:8000/>，应该看到包含以下字段的 JSON：

```json
{"status":"running","service":"DreamCoder - AI游戏生成系统"}
```

OpenAPI 文档位于 <http://localhost:8000/docs>。首次启动会自动在 `backend/` 下创建 SQLite 数据库和表。

## 4. 启动前端

在第二个终端中，从仓库根目录执行：

```bash
cd frontend
npm install
npm run dev
```

### 检查点：工作区已打开

访问 <http://localhost:5173>。开发模式请求验证码时，后端会生成一次性本地验证码，前端自动填入；无需 SMTP 或短信账号。

该便利模式只适合本机。公开部署必须使用 `AUTH_DELIVERY_MODE=external` 并配置真实邮件或短信渠道。

## 5. 生成并继续修改

注册、登录后输入：

> 生成一个复古像素风贪吃蛇游戏，支持方向键控制、计分、暂停和重新开始。

生成结束后确认可以查看文件并打开预览，然后继续输入：

> 保留原有玩法，增加最高分记录和速度逐渐提升的机制。

第二次 Generation Run 会把项目已有文件作为输入。这是 DreamCoder 与单轮代码回答的关键区别。

## 不调用模型先检查界面

如果暂时没有 Key，可以运行三个确定性示例：

```bash
cd DreamCoder
python -m http.server 4173
```

打开 <http://localhost:4173/examples/>。示例不使用外部资源，也不代表模型的固定质量。

## 常见问题

### `LLM_PROVIDER=... requires ..._API_KEY`

当前 provider 对应的 Key 为空。检查 `backend/.env` 的变量名，并确认启动后端时工作目录是 `backend/`。

### Provider 返回 model not found

模型 ID 已下线、账号无权限或 Base URL 不匹配。在官方模型目录确认可用 ID，再覆盖 `DEEPSEEK_MODEL`、`OPENAI_MODEL` 或 `QWEN_MODEL`。

### `npm` 提示 Node 版本不兼容

Vite 7 要求 Node.js 20.19+ 或 22.12+。升级 Node 后删除失败安装产生的 `frontend/node_modules`，再运行 `npm install`。

### 端口 8000 或 5173 被占用

为后端改用 `uvicorn main:app --reload --port 8001`，并在启动前端前设置 `VITE_API_BASE_URL=http://localhost:8001`。也可以先停止占用默认端口的进程。

### Windows 无法执行 `Activate.ps1`

可以不激活环境，直接调用虚拟环境中的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## 下一步

- [理解架构与模块边界](./architecture.md)
- [了解生成内容的安全边界](./security.md)
- [准备托管部署](./deployment.md)
- [查看 Roadmap](../ROADMAP.md)
