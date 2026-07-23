---
name: playtest-web2d-game
description: Use when verifying controls, rules, scene transitions, collisions, win/loss paths, restart behavior, HUD readability, responsive layout, or regressions in a browser-native 2D game.
---

# Playtest a Web 2D Game

Test two independent surfaces: structured gameplay truth and the player's visual experience. A passing screenshot cannot prove rules; passing state assertions cannot prove readability.

## Workflow

1. Call `web2d_project_inspect` and identify the start command, promised inputs, Bridge coverage, tests, and target viewports.
2. Start the game with the host Agent's terminal. Call `web2d_session_start` with a fixed seed and representative viewport.
3. Call `web2d_observe`. Stop if the state omits facts required to distinguish the claim being tested; add the smallest truthful adapter first.
4. Write one-purpose scenarios using [scenario design](references/scenario-design.md). Cover the main loop first, then failure/restart and changed behavior.
5. Use native `key` or `pointer` actions to test control wiring. Use `bridge` actions for deterministic domain setup or rule paths. Never let semantic dispatch become a substitute for testing promised controls.
6. Run `web2d_scenario_run`; inspect the exact failed step, actual value, and final state. Repeat with the same seed to detect uncontrolled time or randomness.
7. Use the host browser or capture capability for the checks in [visual quality](references/visual-quality.md): first playable screen, action feedback, HUD/playfield balance, overlays, resize, and relevant mobile states.
8. Call `web2d_quality_check`; review page exceptions, console errors, failed resources, Bridge readiness, and render surface separately.
9. Stop with `web2d_session_stop`. Report scenarios, seeds, assertions, visual viewports, findings by severity, and untested risks.

## Evidence Rules

- Every gameplay claim requires observed initial state, actions, and an assertion.
- Every visual claim requires a representative rendered state at the intended viewport.
- Keep scenarios short enough that one failure identifies one behavior.
- Avoid exact floating-point positions, array order, and frame counts unless they are part of the contract.
- Record nondeterminism instead of masking it with longer waits.
- Do not add screenshot or generic browser tools to Web2DKit; use the host Agent's existing capability.

## Completion Gate

Finish when the requested gameplay path passes twice with the same seed, native controls are exercised where promised, runtime diagnostics are reviewed, and relevant visual states are inspected independently.
