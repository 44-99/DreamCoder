---
name: build-web2d-game
description: Design, implement, or extend browser-native 2D games with a testable game-state boundary and Web2DKit Game Bridge. Use for HTML/CSS/Canvas/SVG/WebGL-2D games, including projects using Phaser, PixiJS, Kaboom, Excalibur, React, Vue, or vanilla JavaScript/TypeScript; do not use for Unity, Unreal, Godot, Three.js 3D, or editor-dependent engine workflows.
---

# Build a Web 2D Game

Build around the player's loop and observable game rules, not around a preferred framework.

## Workflow

1. Call `web2d_project_inspect` before choosing architecture or dependencies.
2. State the target player, core loop, input methods, win/loss rules, and one smallest playable milestone.
3. Select the least complex browser-native stack that satisfies those requirements. Do not add a framework solely for portfolio value.
4. Separate authoritative game state and rule updates from rendering. Keep state JSON-serializable.
5. Implement the playable milestone, including restart, pause/focus behavior where relevant, and bounded asset loading failures.
6. Install `window.__WEB2D_GAME__` using [references/bridge-integration.md](references/bridge-integration.md).
7. Start the game using its documented command. Do not ask Web2DKit to execute arbitrary shell commands.
8. Call `web2d_session_start`, then `web2d_observe` to prove the bridge reports the real initial state.
9. Exercise the core loop with `web2d_act` or `web2d_scenario_run`. Assert rule outcomes, not merely the absence of console errors.
10. Run repository tests and `web2d_quality_check`. Report the playable milestone, evidence, and remaining unsupported behavior.

## Design constraints

- Treat DOM, Canvas, SVG, and WebGL-2D as renderers; keep rules observable independently of pixels.
- Prefer semantic bridge actions for rules and native key/pointer actions for input wiring.
- Make `reset({ seed })` produce a known starting state. Route gameplay randomness through a seedable source when determinism matters.
- Expose stable IDs for scenes and entities. Do not expose framework objects, DOM nodes, textures, circular references, or secrets.
- Never claim support from a screenshot alone. Require structured state plus at least one gameplay assertion.
- Preserve the host Agent's responsibilities for source editing, terminal use, Git, and generic browser inspection.

## Completion gate

Finish only when the game starts, the bridge is discoverable, one complete player loop is playable, its state transition is asserted, runtime/resource errors are reviewed, and the exact verification commands are recorded.
