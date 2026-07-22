# DreamCoder quickstart: generate your first web game in ten minutes

This guide gets a first-time contributor from clone to one describe-generate-preview loop with the minimum required stack. Add Docker or hosted infrastructure only after that loop works.

| Requirement | Version | Check |
|---|---|---|
| Git | Any recent version | `git --version` |
| Python | 3.11+ | `python --version` |
| Node.js | 20.19+ or 22.12+ | `node --version` |
| npm | Bundled with Node.js | `npm --version` |
| Model credentials | DeepSeek, OpenAI, or Qwen | Create in the provider console |

Docker, PostgreSQL, Redis, and ChromaDB are not local prerequisites.

## 1. Clone and create the environment file

```bash
git clone https://github.com/44-99/DreamCoder.git
cd DreamCoder
```

macOS / Linux:

```bash
cp backend/.env.example backend/.env
```

Windows PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

## 2. Configure one model provider

Edit `backend/.env`. The example defaults to DeepSeek:

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your-key
```

For OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

For Qwen:

```env
LLM_PROVIDER=qwen
QWEN_API_KEY=your-key
```

See [`backend/.env.example`](../backend/.env.example) for model IDs, base URLs, and optional variables. Provider catalogs evolve. If the provider reports that a model does not exist, verify the official catalog and override the relevant `*_MODEL` value.

## 3. Start the backend

macOS / Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

### Checkpoint: the backend works

Open <http://localhost:8000/>. The JSON response should contain:

```json
{"status":"running","service":"DreamCoder - AI游戏生成系统"}
```

OpenAPI documentation is available at <http://localhost:8000/docs>. The first startup creates the SQLite database and tables under `backend/` automatically.

## 4. Start the frontend

From the repository root in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

### Checkpoint: the workspace opens

Open <http://localhost:5173>. In development, requesting a verification code creates a local one-time code and automatically fills it in the UI, so no SMTP or SMS account is needed.

This convenience is for local development only. Public deployments must use `AUTH_DELIVERY_MODE=external` and configure a real email or SMS channel.

## 5. Generate and iterate

After registering and signing in, enter:

> Build a retro pixel-art Snake game with arrow-key controls, scoring, pause, and restart.

When generation finishes, inspect the files and open the preview. Then enter:

> Preserve the existing gameplay and add a high-score record plus gradually increasing speed.

The second Generation Run receives the project's existing files. That continuation is the key difference from a one-shot code response.

## Check the product shape without a model call

If you do not have a key yet, run the deterministic examples:

```bash
cd DreamCoder
python -m http.server 4173
```

Open <http://localhost:4173/examples/>. The examples use no external assets and do not claim a model's fixed quality.

## Troubleshooting

### `LLM_PROVIDER=... requires ..._API_KEY`

The selected provider's key is empty. Check the variable name in `backend/.env` and start the backend from the `backend/` directory.

### The provider reports `model not found`

The ID may have been retired, your account may lack access, or the base URL may not match. Verify the official catalog and override `DEEPSEEK_MODEL`, `OPENAI_MODEL`, or `QWEN_MODEL`.

### npm reports an unsupported Node version

Vite 7 requires Node.js 20.19+ or 22.12+. Upgrade Node, remove `frontend/node_modules` created by the failed install, and run `npm install` again.

### Port 8000 or 5173 is busy

Run the backend with `uvicorn main:app --reload --port 8001` and set `VITE_API_BASE_URL=http://localhost:8001` before starting the frontend, or stop the process using the default port.

### PowerShell blocks `Activate.ps1`

Call the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## Next steps

- [Understand the architecture](./architecture.en.md)
- [Review generated-content security](./security.en.md)
- [Prepare a hosted deployment](./deployment.en.md)
- [See the roadmap](../ROADMAP.md)
