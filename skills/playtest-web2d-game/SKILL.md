---
name: playtest-web2d-game
description: Playtest browser-native 2D games through deterministic actions, structured state observations, gameplay assertions, and saved regression scenarios. Use when verifying controls, rules, win/loss conditions, pause and focus behavior, scene transitions, collision outcomes, or bug fixes in HTML/Canvas/SVG/WebGL-2D games.
---

# Playtest a Web 2D Game

Turn a gameplay claim into a reproducible state transition and explicit assertions.

## Workflow

1. Call `web2d_project_inspect` and identify the documented start command, bridge coverage, and test scripts.
2. Start the game using the host Agent's terminal, then call `web2d_session_start` with a fixed seed.
3. Call `web2d_observe`. If the bridge is absent or state is incomplete, stop and add the smallest truthful bridge adapter before testing rules.
4. Write a scenario with one purpose using [references/scenario-design.md](references/scenario-design.md).
5. Prefer native `key` or `pointer` actions for control wiring. Prefer `bridge` actions for rule-level reproducibility. Use frame waits only when timing is part of the contract.
6. Run `web2d_scenario_run`. Inspect every failed assertion and the final state; do not retry with random timing until it happens to pass.
7. Run `web2d_quality_check` and review console, page, and resource failures separately from gameplay correctness.
8. Re-run the same scenario with the same seed. Treat inconsistent results as a determinism defect.
9. Stop with `web2d_session_stop` and report the scenario, seed, assertions, result, and untested risks.

## Evidence rules

- A rendered frame proves appearance only; it does not prove collision, score, health, lifecycle, or victory rules.
- A lack of exceptions proves only that no captured exception occurred.
- Every gameplay claim needs an observed initial state, an action sequence, and a final assertion.
- Keep scenarios short enough that a failure identifies one behavior.
- Record known nondeterministic systems instead of hiding them with long waits.

## Completion gate

Finish only when the requested rule has a deterministic scenario, the expected state transition passes twice, runtime diagnostics are reviewed, and failures include an exact step and actual value.
