---
name: design-web2d-game
description: Use when turning a browser-native 2D game idea, clone request, vague prototype, or existing concept into a scoped and testable game contract before implementation.
---

# Design a Web 2D Game

Convert the request into a small game worth playing and a contract an Agent can later verify. Decide the player experience before choosing a framework.

## Workflow

1. For an existing repository, call `web2d_project_inspect` before proposing a rewrite. Preserve its stack unless a measured constraint requires change.
2. Define the target player, device, input modes, expected session length, and intended scope.
3. Lock the fantasy, primary verbs, immediate objective, failure state, restart path, and reward.
4. Add the smallest pressure, escalation, variety, and feedback needed to make the loop interesting beyond its first interaction.
5. Choose one vertical slice that includes onboarding, play, success or failure, and replay. Defer features that do not strengthen that slice.
6. Set an art, audio, camera, HUD, and motion direction. Distinguish intentional procedural visuals from temporary programmer art.
7. Write a state contract: stable scenes, entities, objectives, actions, and lifecycle facts that `window.__WEB2D_GAME__` must expose.
8. Write two to five acceptance scenarios as initial state → player actions → observable outcome. Map each outcome to `web2d_observe`, `web2d_act`, or `web2d_scenario_run` evidence.
9. Produce the compact game contract in [references/game-design-contract.md](references/game-design-contract.md), then hand implementation to `build-web2d-game`.

## Design Rules

- Treat “make a platformer/puzzle/shooter” as a genre constraint, not a complete design.
- Prefer one complete loop over many disconnected mechanics.
- Keep rules separate from presentation so the Agent can inspect and test them.
- Do not select Phaser, PixiJS, React, or another stack for résumé value.
- Do not promise generated assets, multiplayer, procedural content, or mobile support unless the slice budgets and verifies them.
- Use screenshots to judge appearance, never to prove hidden rules.

## MCP Evidence Map

| Design claim | Required later evidence |
|---|---|
| The project fits the existing stack | `web2d_project_inspect` |
| The initial scene and rules are known | `web2d_observe` |
| Controls reach the game | native `web2d_act` actions |
| Win, loss, scoring, inventory, or collisions work | `web2d_scenario_run` assertions |
| Startup and resources are healthy | `web2d_quality_check` |

## Completion Gate

Finish when the contract names the player, loop, pressure, progression, visual direction, vertical slice, observable state, and acceptance scenarios. Surface unresolved product choices instead of hiding them in implementation details.
