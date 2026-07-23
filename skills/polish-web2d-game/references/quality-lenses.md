# Quality lenses

Choose one or two lenses per pass. Broad undirected polish produces noise and regressions.

| Lens | Questions | Evidence |
|---|---|---|
| Readability and UI | Can the player find the objective, threats, status, and next action? Does the HUD protect play? | screenshots at representative states and viewports |
| Game feel | Do movement, impact, reward, danger, and failure have distinct timing and feedback? | native input, state assertions, short video/screenshots |
| Visual cohesion | Do palette, scale, anchors, silhouettes, animation, camera, and effects agree? | asset inspection and rendered states at game scale |
| Audio | Are start, action, impact, reward, danger, UI, and pause states supported without fatigue? | interaction review, focus/audio-unlock checks |
| Responsive/accessibility | Do promised inputs, viewports, focus, contrast, reduced motion, and non-color cues work? | viewport/input matrix and visual review |
| Performance | Are frame pacing, entity counts, allocations, assets, and lifecycle cleanup within an explicit budget? | metrics, browser profiling, `web2d_quality_check` |

## Before/after claim template

```text
Problem: what the player experiences
State/setup: seed, scene, viewport, and actions
Change: the smallest selected quality intervention
Rule guard: scenario and assertions that must remain unchanged
Visual evidence: what the rendered comparison must show
Residual risk: devices, assets, inputs, or content not reviewed
```

Avoid “more polish” as a completion criterion. Name the player-visible outcome.
