<p align="right">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<div align="center">
  <img src="./docs/assets/web2dkit-logo.svg" alt="Web2DKit logo" width="96" />
  <h1>Web2DKit</h1>
  <p><strong>MCP tools and Agent Skills for building, playtesting, and debugging browser-native 2D games.</strong></p>
  <p>Give Codex, Claude Code, and other MCP-compatible coding agents structured game state—not another prompt wrapper.</p>

  [![CI](https://github.com/44-99/Web2DKit/actions/workflows/ci.yml/badge.svg)](https://github.com/44-99/Web2DKit/actions/workflows/ci.yml)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
  [![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933.svg?logo=node.js&logoColor=white)](https://nodejs.org/)
</div>

## Why Web2DKit?

Coding agents can already write game code, edit files, run commands, and inspect screenshots. The missing layer is **game semantics**: what scene is active, whether a collision changed health correctly, which step broke a rule, and whether the same input can reproduce the failure.

Web2DKit adds that layer through a small Game Bridge and bounded MCP tools:

```text
request → coding agent → source changes
                         ↓
          Web2DKit Skill workflow
                         ↓
fixed seed → actions → structured state → assertions → regression scenario
```

## What works today

- Inspect a Web 2D project without escaping its configured filesystem root.
- Start a controlled Playwright session with a fixed random seed.
- Read JSON-serializable scenes, entities, rules, score, and metrics through the Game Bridge.
- Perform bounded keyboard, pointer, wait/frame-step, and semantic bridge actions.
- Run deterministic scenarios with step and final assertions.
- Report runtime errors, failed resources, bridge readiness, and render-surface health.
- Guide agents with three operational Skills: build, playtest, and debug.
- Load as a Codex plugin or Claude Code plugin from the same repository.

Web2DKit does **not** provide chat history, model routing, arbitrary shell execution, generic file editing, or a replacement web IDE. The host coding agent already owns those capabilities.

## Scope

Web2DKit targets browser-native 2D games built with HTML/CSS/DOM, Canvas 2D, SVG, Web Audio, or WebGL-based 2D rendering. Vanilla JavaScript/TypeScript and lightweight frameworks such as Phaser, PixiJS, Kaboom, and Excalibur fit this boundary.

Unity WebGL, Unreal Engine, Godot, Three.js 3D scenes, and editor-dependent engine pipelines are intentionally out of scope.

The v0.1 bridge is framework-neutral. Project detection covers common Web 2D stacks; deeper Phaser and PixiJS adapters are planned, not claimed as complete.

## Verify it locally

Requires Node.js 22+.

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

This runs unit tests plus a real Chromium scenario against the included [Bridge demo](./examples/bridge-demo/).

For local plugin installation and first use, follow [Getting started](./docs/getting-started.md).

## Game Bridge in one minute

Expose the authoritative state already owned by your game:

```js
window.__WEB2D_GAME__ = {
  describe: () => ({ protocolVersion: "1", name: "my-game" }),
  getState: () => structuredClone(gameState),
  reset: ({ seed } = {}) => resetGame(seed ?? 1),
  dispatch: ({ name, payload }) => dispatchGameAction(name, payload)
};
```

Then an agent can prove a rule with `web2d_session_start` → `web2d_observe` → `web2d_scenario_run`, instead of guessing from pixels. See the [Bridge protocol](./docs/bridge-protocol.md) and [MCP tool reference](./docs/mcp-tools.md).

## Documentation

- [Getting started](./docs/getting-started.md)
- [Architecture](./docs/architecture.md)
- [Game Bridge protocol](./docs/bridge-protocol.md)
- [MCP tools](./docs/mcp-tools.md)
- [Security boundaries](./docs/security.md)
- [Roadmap](./ROADMAP.md)
- [Contributing](./CONTRIBUTING.md)

## Status

Web2DKit is an early, working foundation. The included browser integration test proves the core state/action/assertion loop, but the project still needs real-world adapters, saved scenario files, performance budgets, and feedback from 2D game developers before a stable release.

Web2DKit is available under the [MIT License](./LICENSE).
