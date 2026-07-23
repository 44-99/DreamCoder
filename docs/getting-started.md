# Getting started

Web2DKit runs locally over MCP stdio. It does not require a model API key, database, Docker service, or hosted account.

## Prerequisites

- Node.js 22 or newer
- Codex, Claude Code, or another MCP-compatible coding agent
- A browser-native 2D game served over `http://` or `https://`

## Build and verify Web2DKit

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

`npm run validate` type-checks, runs unit and real-browser integration tests, then builds `dist/server.js`.

## Claude Code plugin development

Run Claude Code with the repository as a local plugin:

```bash
claude --plugin-dir /absolute/path/to/Web2DKit
```

The root `.mcp.json` starts `dist/server.js`, sets `WEB2DKIT_ROOT` to the active Claude project, and exposes the bundled Skills. Run `npm run build` after changing Web2DKit source, then reload plugins.

## Codex local development

The repository includes a validated `.codex-plugin/plugin.json` for the five Skills. Until Web2DKit is published as an installable package, register the built MCP server with an explicit absolute path:

```bash
codex mcp add web2dkit -- node /absolute/path/to/Web2DKit/dist/server.js
```

Codex supplies the active project root to the server. The source-development verification record documents the current split between Skill installation and explicit MCP registration; marketplace packaging remains a separate roadmap gate.

## First deterministic check

1. Start the target game with its own development command.
2. Ask the agent to call `web2d_project_inspect`.
3. Add the Game Bridge if inspection reports it missing.
4. Call `web2d_session_start` with the local game URL and `seed: 42`.
5. Call `web2d_observe` and verify the initial state.
6. Run one short `web2d_scenario_run` with a state assertion.
7. Call `web2d_quality_check`, then `web2d_session_stop`.

Once the loop works, save its regression coverage as strict `*.web2d.json` files and run them against an already running game:

```bash
node /absolute/path/to/Web2DKit/dist/cli.js run --url http://127.0.0.1:4173 web2dkit/scenarios
```

See [Acceptance scenarios and CLI](./scenarios.md) for the schema, reporters, and evidence boundary.

The included example can be served with any static HTTP server. For example:

```bash
npx http-server examples/bridge-demo -p 4173
```

Then start a Web2DKit session at `http://127.0.0.1:4173`.

## Common failures

- `BROWSER_NOT_INSTALLED`: run `npx playwright install chromium` in the Web2DKit checkout.
- `BRIDGE_NOT_AVAILABLE`: expose `window.__WEB2D_GAME__` and reload or restart the session.
- `PROJECT_BOUNDARY_VIOLATION`: use a relative path inside `WEB2DKIT_ROOT`; absolute and parent-traversal paths are rejected.
- `SESSION_NOT_FOUND`: start a new session; stopped and process-local sessions are not persistent.
