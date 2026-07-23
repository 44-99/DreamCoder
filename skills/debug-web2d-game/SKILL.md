---
name: debug-web2d-game
description: Diagnose and fix reproducible browser-native 2D gameplay defects using fixed seeds, structured state traces, runtime diagnostics, and regression scenarios. Use for broken controls, incorrect rules, collision bugs, scene lifecycle leaks, pause/focus problems, nondeterministic failures, resource errors, or state/render divergence in Web 2D games.
---

# Debug a Web 2D Game

Reduce the report to the first incorrect state transition, fix its owning layer, and preserve the reproduction as a regression scenario.

## Workflow

1. Translate the report into expected initial state, minimal actions, expected result, and observed result.
2. Call `web2d_project_inspect`, start the game, then call `web2d_session_start` with a recorded seed.
3. Call `web2d_observe` before acting. Verify that the bridge exposes every state field needed to distinguish the hypotheses.
4. Reproduce with the shortest `web2d_scenario_run` possible. If reproduction depends on uncontrolled waiting, first add deterministic stepping or a domain action.
5. Classify the first failure using [references/failure-layers.md](references/failure-layers.md). Keep input, state/rules, lifecycle, rendering, assets, and performance as separate boundaries.
6. Change the smallest owner of the incorrect transition. Do not rewrite the rendering stack to repair a rule defect.
7. Re-run the exact seed and scenario, then adjacent scenarios and existing tests.
8. Keep the scenario in project test fixtures when it protects a real bug contract.
9. Run `web2d_quality_check`, stop the session, and report root cause, changed boundary, before/after evidence, and remaining uncertainty.

## Debugging rules

- If structured state is correct but pixels are wrong, debug rendering or assets.
- If native input does nothing but bridge dispatch works, debug focus, event mapping, or input lifecycle.
- If both inputs produce the wrong state, debug rules or update order.
- If the same seed and actions diverge, find uncontrolled time, randomness, iteration order, or asynchronous work before tuning waits.
- If a scene works once but fails after restart, inspect subscriptions, timers, retained entities, and teardown.
- Never fix a symptom by weakening the assertion unless the product rule itself changed.

## Completion gate

Finish only when the original scenario fails before the fix, passes after it, passes again with the same seed, and the explanation identifies the first incorrect state transition rather than only the visible symptom.
