# Signal Relay: reproducible end-to-end example

[简体中文](./README.zh-CN.md)

Signal Relay is a small deterministic grid puzzle created with Web2DKit's design, build, playtest, and polish Skills. It is also an executable proof that the MCP server can inspect a real project, initialize its Game Bridge, drive native and semantic inputs, replay scenarios, and verify game rules.

| | |
|---|---|
| Time | 5–10 minutes |
| Requirements | Node.js 22+, Chromium installed through Playwright |
| Stack | TypeScript, DOM/CSS, Vite, Vitest |
| Goal | Activate A → B → C and reach the uplink |

## Run the complete acceptance flow

From the Web2DKit repository root:

```bash
npm ci
npx playwright install chromium
npm run example:signal-relay:e2e
```

The command builds Web2DKit, starts Signal Relay on an available local port, launches the real MCP server over stdio, runs the scenarios, prints a compact JSON result, and shuts everything down.

Expected result:

```json
{
  "ok": true,
  "tools": 8,
  "seed": 42,
  "nativeInput": true,
  "deterministicReplay": true,
  "winningScore": 570,
  "pauseScenario": true,
  "cliScenarioSuite": true,
  "qualityCheck": true
}
```

## Inspect the game manually

```bash
npm run example:signal-relay:dev
```

Open the URL printed by Vite. Use Arrow keys or WASD to move, Escape to pause, and R to restart. Touch controls appear on narrow screens.

## How the proof is structured

1. [`docs/game-contract.md`](./docs/game-contract.md) defines the player promise, loop, scope, presentation, and acceptance scenarios before implementation.
2. [`src/domain.ts`](./src/domain.ts) keeps deterministic rules independent from rendering.
3. [`src/main.ts`](./src/main.ts) renders the game and exposes `window.__WEB2D_GAME__`.
4. [`tests/domain.test.ts`](./tests/domain.test.ts) checks rule-level behavior without a browser.
5. [`web2dkit/scenarios`](./web2dkit/scenarios/) stores three strict, versioned Acceptance Scenarios owned by the game project.
6. [`scripts/run-web2dkit-acceptance.mjs`](./scripts/run-web2dkit-acceptance.mjs) runs the shared CLI suite and exercises the built Web2DKit MCP server against the same running game.

To run only the Git-owned scenario suite, start the game with `npm run example:signal-relay:dev`, then use the printed URL:

```bash
node dist/cli.js run --url http://127.0.0.1:5173 examples/signal-relay/web2dkit/scenarios
```

The MCP assertions prove structured game state and rules. Visual inspection remains a separate host-browser responsibility because screenshots and semantic state answer different questions.

## Troubleshooting

### Chromium is missing

```bash
npx playwright install chromium
```

### `dist/server.js` is missing

Use the root command `npm run example:signal-relay:e2e`; it builds Web2DKit before starting acceptance.

### A scenario fails

Read the failing assertion and step in the command output, then run `npm run example:signal-relay:dev` for visual inspection. Do not replace a failed rule assertion with screenshot-only evidence.
