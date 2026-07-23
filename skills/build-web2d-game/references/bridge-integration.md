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
