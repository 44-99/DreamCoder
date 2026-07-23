# Game Bridge protocol v1

The Game Bridge is the semantic boundary between Web2DKit and a running browser-native 2D game.

## Global entry point

The game exposes `window.__WEB2D_GAME__` before Web2DKit observes state.

## Required methods

### `describe()`

Return `{ protocolVersion: "1", name, framework?, capabilities? }`. Keep names stable across runs.

### `getState()`

Return a JSON object containing authoritative game facts. The result must serialize without custom replacers and must not contain DOM nodes, framework instances, functions, binary assets, cycles, secrets, or personal data.

### `reset({ seed? })`

Return the game to a known initial state. When the game uses randomness, the same seed and actions should reproduce the same rule-relevant state.

## Optional methods

### `dispatch({ name, payload? })`

Apply a semantic domain action through the same rule path used by the game. This is for deterministic operations such as `select-card`, `end-turn`, or `spawn-test-wave`; it must not become an unrestricted script evaluator.

### `step(frames)`

Advance a fixed number of logical frames. Use this for simulations whose correctness depends on game-loop timing. If absent, Web2DKit converts frame waits to approximate wall-clock waits and reports less deterministic behavior.

### `getMetrics()`

Return JSON metrics such as active entity count, logical ticks, draw calls, or domain-specific budgets.

## State design

Prefer stable domain fields:

```json
{
  "scene": "level-1",
  "status": "playing",
  "player": { "id": "player", "x": 128, "y": 320, "health": 80 },
  "entities": [{ "id": "slime-3", "type": "enemy", "state": "chasing" }],
  "score": 120,
  "paused": false
}
```

Do not mirror an entire engine scene graph. Expose only what a developer needs to understand and verify player-visible rules.

## Compatibility

Protocol additions must remain optional within v1. Breaking field or method semantics requires a new protocol version. Framework adapters should translate to this contract instead of changing MCP tool names.
