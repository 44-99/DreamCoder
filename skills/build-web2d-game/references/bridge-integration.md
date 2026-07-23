# Game Bridge integration

Expose one framework-neutral object on the game page:

```ts
window.__WEB2D_GAME__ = {
  describe: () => ({
    protocolVersion: "1",
    name: "my-game",
    framework: "Canvas 2D",
    capabilities: ["state", "reset", "dispatch", "step"]
  }),
  getState: () => structuredClone(gameState),
  reset: ({ seed } = {}) => resetGame(seed ?? 1),
  dispatch: ({ name, payload }) => dispatchGameAction(name, payload),
  step: (frames) => advanceFixedFrames(frames),
  getMetrics: () => ({ activeEntities: entities.length })
};
```

Only `describe`, `getState`, and `reset` are required. Add `dispatch`, `step`, and `getMetrics` when the game can implement them truthfully.

Return stable, domain-relevant facts from `getState()`: current scene and lifecycle status; player state; rule-relevant entities; score, turns, objectives, and win/loss conditions; input and pause/focus state when relevant.

Keep render-only details out unless a regression depends on them. Never return DOM nodes, engine instances, binary assets, functions, cyclic objects, tokens, or user data.

Use native key and pointer actions to verify input wiring. Use `dispatch` for deterministic domain actions that otherwise depend on timing or coordinates. Both must update the same authoritative state.

## Framework boundaries

- **Phaser**: keep the Bridge adapter outside scene rules. Read serializable simulation state; translate dispatches into the same action queue consumed by scene input. Reset scene-owned listeners, timers, and tweens during restart.
- **PixiJS**: Pixi is the renderer, so keep the authoritative model in application code. Do not serialize Containers, Sprites, Textures, or Tickers.
- **Canvas 2D**: expose the model updated by the loop, not drawing commands or canvas pixels. Implement logical frame stepping only when the update loop can advance without wall-clock time.
- **DOM/SVG**: observe the domain model rather than scraping text/classes as game state. Native pointer and keyboard actions should still prove the view is wired to the model.

Bridge integration is not a debug backdoor. Do not add arbitrary JavaScript evaluation, direct mutation of internal objects, or actions that bypass the rules being tested.
