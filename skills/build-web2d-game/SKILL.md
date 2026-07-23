---
name: build-web2d-game
description: Use when implementing, extending, or completing browser-native 2D games in HTML, Canvas, SVG, Phaser, PixiJS, Excalibur, Kaboom, React, Vue, or vanilla JavaScript/TypeScript.
---

# Build a Web 2D Game

Build the smallest complete player loop, then prove it through the same state and rule boundary the game owns. Route vague concepts through `design-web2d-game` first.

## Workflow

1. Call `web2d_project_inspect`. Read the existing package scripts, framework, entry points, tests, and Bridge coverage before choosing structure or dependencies.
2. Confirm the game contract: player, verbs, objective, pressure, failure/restart, progression, visual direction, inputs, and acceptance scenarios. Use [game production](references/game-production.md) when any of these are weak.
3. Choose the least complex compatible stack using [stack selection](references/stack-selection.md). Preserve an existing stack unless migration has a concrete payoff.
4. Separate authoritative serializable rules from rendering, framework objects, input devices, UI, audio, and asset loading. Keep scenes and renderer callbacks thin.
5. Create an explicit action map. Route keyboard, pointer, touch, and gamepad inputs into domain actions rather than duplicating game rules per device.
6. Define an asset manifest and art constraints before tuning collisions, anchors, camera framing, or UI around temporary dimensions.
7. Implement one vertical slice: first actionable screen → core loop → opposition or constraint → success/failure → restart. Add only the feedback and content required to make that slice readable and satisfying.
8. Install `window.__WEB2D_GAME__` early using [Bridge integration](references/bridge-integration.md). Expose stable domain state, not renderer internals.
9. Start the game with its documented command. Call `web2d_session_start` with a fixed seed, then `web2d_observe` to validate the real initial state.
10. Exercise native controls with `web2d_act`; exercise deterministic rule paths with `web2d_scenario_run`. Assert the complete loop and restart path.
11. Use the host Agent's browser/screenshot capability for visual review. Do not add a duplicate screenshot MCP tool.
12. Run repository tests and `web2d_quality_check`. Report exactly what is playable, what evidence passed, and what remains outside the slice.

## Architecture Rules

- Simulation owns rules, entities, time, score, progression, saveable state, and lifecycle.
- Rendering owns sprites, cameras, animation playback, particles, DOM views, and effects.
- Asset keys and entity IDs are stable; filenames and array order are not public APIs.
- `reset({ seed })` creates a known state. Route meaningful randomness through a seedable source.
- Use DOM for text-heavy menus and accessible controls when it fits the selected stack; protect the playfield from dashboard-like chrome.
- Clean up listeners, timers, tweens, input bindings, and renderer objects on scene shutdown and restart.
- Never claim a feature works because the page rendered or produced no exception.

## Completion Gate

Finish only when the vertical slice is playable from its intended inputs, the Bridge reports truthful state, one complete loop and restart are asserted with a fixed seed, runtime/resource failures are reviewed, and visual claims have separate visual evidence.
