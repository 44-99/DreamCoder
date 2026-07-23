# 入门指南

Web2DKit 通过本地 MCP stdio 运行，不需要模型 API Key、数据库、Docker 服务或在线账号。

## 环境要求

- Node.js 22+
- Codex、Claude Code 或其他兼容 MCP 的编程 Agent
- 一个通过 `http://` 或 `https://` 运行的浏览器原生 2D 游戏

## 构建并验证

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

`npm run validate` 会完成 TypeScript 检查、单元测试、真实浏览器集成测试和 MCP Server 构建。

## Claude Code 本地插件

```bash
claude --plugin-dir /absolute/path/to/Web2DKit
```

根目录 `.mcp.json` 会启动 `dist/server.js`，把当前 Claude 项目设置为允许访问的项目根，并加载五个 Skills。修改 Web2DKit 源码后先执行 `npm run build`，再重新加载插件。

## Codex 本地开发

仓库已经包含经过验证的 `.codex-plugin/plugin.json`，用于加载五个 Skills。在 Web2DKit 发布为可安装包之前，请使用绝对路径注册构建后的 MCP Server：

```bash
codex mcp add web2dkit -- node /absolute/path/to/Web2DKit/dist/server.js
```

Codex 会把当前项目根传给 MCP Server。源码开发验收记录说明了当前“Skills 安装 + 显式 MCP 注册”的边界；Marketplace 打包仍是后续独立门槛。

## 第一次确定性验证

1. 使用游戏自己的命令启动开发服务器。
2. 调用 `web2d_project_inspect`。
3. 如果报告缺少 Bridge，先接入 `window.__WEB2D_GAME__`。
4. 使用本地 URL 与固定 `seed: 42` 调用 `web2d_session_start`。
5. 调用 `web2d_observe` 验证初始状态。
6. 用 `web2d_scenario_run` 执行一个短场景并断言状态。
7. 调用 `web2d_quality_check`，最后调用 `web2d_session_stop`。

核心循环跑通后，把回归验证保存为严格的 `*.web2d.json` 文件，并连接到已经运行的游戏：

```bash
node /absolute/path/to/Web2DKit/dist/cli.js run --url http://127.0.0.1:4173 web2dkit/scenarios
```

场景格式、报告器和证据边界见[验收场景与 CLI](./scenarios.md)。

## 常见错误

- `BROWSER_NOT_INSTALLED`：在 Web2DKit 目录执行 `npx playwright install chromium`。
- `BRIDGE_NOT_AVAILABLE`：接入 `window.__WEB2D_GAME__` 后重新加载或重启会话。
- `PROJECT_BOUNDARY_VIOLATION`：只能使用 `WEB2DKIT_ROOT` 内的相对路径。
- `SESSION_NOT_FOUND`：会话已经停止或 MCP 进程已重启，需要重新创建。
