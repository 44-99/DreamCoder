<p align="center">
  <a href="./README.md"><strong>English</strong></a> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<div align="center">
  <img src="./docs/assets/web2dkit-logo.svg" alt="Web2DKit logo" width="112" />
  <h1>Web2DKit</h1>
  <p><strong>The game-development layer for coding agents.</strong></p>
  <p>Build better browser-native 2D games with Codex, Claude Code, and other coding agents—from a focused game contract to deterministic playtests.</p>

  <a href="https://github.com/44-99/Web2DKit/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/44-99/Web2DKit/ci.yml?branch=main&style=flat-square&label=CI" alt="CI status" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-0f766e?style=flat-square" alt="MIT License" /></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-22%2B-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node.js 22 or newer" /></a>
  <img src="https://img.shields.io/badge/MCP-compatible-7c3aed?style=flat-square" alt="MCP compatible" />
  <img src="https://img.shields.io/badge/Agent_Skills-included-2563eb?style=flat-square" alt="Agent Skills included" />
  <a href="https://github.com/44-99/Web2DKit/stargazers"><img src="https://img.shields.io/github/stars/44-99/Web2DKit?style=flat-square" alt="GitHub stars" /></a>

  <p>
    <a href="#quick-start">Quick start</a> ·
    <a href="#skill-guided-workflow">Skills</a> ·
    <a href="./docs/mcp-tools.md">MCP tools</a> ·
    <a href="./docs/bridge-protocol.md">Game Bridge</a> ·
    <a href="./ROADMAP.md">Roadmap</a>
  </p>
</div>

---

## Why Web2DKit?

Coding agents already write code, run terminals, and inspect screenshots. A screenshot, however, cannot prove that a collision removed the right health, a puzzle reached a valid state, or a restart cleared every timer.

Web2DKit adds the missing game-development feedback loop:

| Agent alone | Agent + Web2DKit |
|---|---|
| Generates mechanics from a prompt | Starts from a scoped player loop and quality contract |
| Guesses hidden state from pixels | Reads structured scenes, entities, objectives, and lifecycle state |
| Clicks coordinates and waits | Uses bounded native input and semantic game actions |
| Stops when the page runs | Proves rules with fixed seeds and explicit assertions |
| Re-discovers the workflow next session | Replays short regression scenarios through reusable Skills |

```text
game idea → design Skill → coding agent edits the game
                                  ↓
visual review ← Game Bridge ← MCP actions, observations, and assertions
       └──────────────────── iterate ────────────────────┘
```

Web2DKit does not replace the coding agent, browser, terminal, or renderer. It gives them a shared, testable language for 2D game rules.

## What ships

- **Five game-development Skills** for design, implementation, playtesting, debugging, and polish.
- **Eight bounded MCP tools** for project inspection, browser sessions, observation, actions, assertions, scenarios, and runtime quality checks.
- **A framework-neutral Game Bridge** that exposes authoritative JSON state without leaking renderer objects or arbitrary JavaScript execution.
- **Codex and Claude Code plugin manifests** backed by the same local Node.js server.

## Skill-guided workflow

| Skill | When it helps | MCP evidence |
|---|---|---|
| `design-web2d-game` | Turn an idea into a player loop, vertical slice, state contract, and acceptance scenarios | project inspection and an evidence-ready design |
| `build-web2d-game` | Implement or extend Canvas, DOM/SVG, Phaser, PixiJS, or similar Web 2D games | observe the initial state and assert a complete loop |
| `playtest-web2d-game` | Verify controls, rules, lifecycle, responsive UI, and regressions | deterministic scenarios plus separate visual review |
| `debug-web2d-game` | Find the first incorrect transition instead of patching the visible symptom | fixed-seed reproduction and regression assertion |
| `polish-web2d-game` | Improve feel, UI, assets, accessibility, or performance without breaking rules | before/after visual evidence plus scenario guards |

The Skills deliberately keep gameplay truth and visual quality as two evidence lanes. Web2DKit handles structured game semantics; the host Agent keeps using its own browser and screenshot capabilities.

## Quick start

Requires Node.js 22+.

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

Then follow [Getting started](./docs/getting-started.md) to load the local plugin in Codex or Claude Code and point it at a running Web 2D game.

Try prompts such as:

```text
Use $design-web2d-game to turn this puzzle idea into a small testable game contract.
Use $build-web2d-game to implement the first complete player loop and verify it.
Use $playtest-web2d-game to prove restart clears the board and score.
```

## Game Bridge in 60 seconds

Expose the serializable state already owned by the game:

```js
window.__WEB2D_GAME__ = {
  describe: () => ({ protocolVersion: "1", name: "my-game" }),
  getState: () => structuredClone(gameState),
  reset: ({ seed } = {}) => resetGame(seed ?? 1),
  dispatch: ({ name, payload }) => dispatchGameAction(name, payload)
};
```

An Agent can then run `web2d_session_start` → `web2d_observe` → `web2d_scenario_run` and prove a gameplay claim instead of inferring it from pixels. See the [Bridge protocol](./docs/bridge-protocol.md) and [MCP tool reference](./docs/mcp-tools.md).

## Scope

Web2DKit targets browser-native 2D games built with DOM/CSS, Canvas 2D, SVG, Web Audio, or WebGL-based 2D renderers. It is designed for vanilla JavaScript/TypeScript and frameworks such as Phaser, PixiJS, Excalibur, and Kaboom.

Unity, Unreal, Godot, Three.js 3D scenes, and editor-dependent pipelines are outside the current scope. Framework detection exists today; deep Phaser and PixiJS adapters remain roadmap work and are not presented as complete.

## Documentation

- [Getting started](./docs/getting-started.md)
- [Architecture](./docs/architecture.md)
- [Game Bridge protocol](./docs/bridge-protocol.md)
- [MCP tool reference](./docs/mcp-tools.md)
- [Security boundaries](./docs/security.md)
- [Roadmap](./ROADMAP.md)
- [Contributing](./CONTRIBUTING.md)

## Project status

Web2DKit is an early working foundation. Its real Chromium integration test proves the state → action → assertion loop. The next credibility gate is validating the workflow in real puzzle, action, and simulation games before a stable release.

MIT licensed. Built for developers who want coding agents to create games they can also understand, play, and verify.
