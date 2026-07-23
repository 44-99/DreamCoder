---
name: polish-web2d-game
description: Use when a browser-native 2D game is playable but still feels like a prototype because of weak feedback, inconsistent art, obstructive UI, rough animation, poor responsive behavior, accessibility gaps, or performance instability.
---

# Polish a Web 2D Game

Improve the player-visible experience without destabilizing proven rules. Measure a baseline, change one quality lens at a time, and preserve deterministic gameplay scenarios.

## Workflow

1. Call `web2d_project_inspect`, start a fixed-seed session, and use `web2d_observe` plus existing scenarios to record the current playable contract.
2. Inspect representative rendered states with the host Agent's browser/capture capability. Rank problems by player impact, not implementation convenience.
3. Select at most two primary lenses from [quality lenses](references/quality-lenses.md): readability/UI, game feel, visual cohesion/assets, audio, responsive/accessibility, or performance.
4. Define a before/after claim for each selected lens and the evidence type it needs. Keep rule claims mapped to MCP state and visual claims mapped to rendered review.
5. Make the smallest coherent changes. Preserve state ownership, action mapping, entity IDs, reset semantics, and existing acceptance scenarios.
6. Exercise the affected path with native `web2d_act` input. Run `web2d_scenario_run` for rule regressions and repeat with the same seed.
7. Inspect the repaired visual states, including overlays and promised viewports. Call `web2d_quality_check` for resource/runtime regressions.
8. Stop the session and report the selected lenses, before/after evidence, performance or accessibility limits, and deliberately deferred polish.

## Rules

- Do not replace deliberate art direction with generic gradients, glass cards, or excessive particles.
- Keep HUD hierarchy subordinate to play; use DOM where text, forms, localization, or focus semantics benefit.
- Use strong motion and audio for meaningful state changes, not every interaction.
- Preserve reduced-motion behavior and input focus under overlays.
- Profile before performance rewrites; cap pools and clean up lifecycle-owned resources.
- Never claim visual improvement from code inspection alone.

## Completion Gate

Finish when the selected quality claims have before/after evidence, the affected gameplay scenario still passes twice with the same seed, native input remains wired, and `web2d_quality_check` introduces no new blocking failure.
