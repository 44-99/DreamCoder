# Scenario design

Define one scenario as a reset seed, ordered actions, optional step assertions, and final assertions:

```json
{
  "name": "player collects the key",
  "seed": 42,
  "steps": [
    {
      "action": { "kind": "key", "key": "ArrowRight" },
      "assertions": [
        { "path": "player.position.x", "operator": "greaterThan", "expected": 100 }
      ]
    },
    {
      "action": { "kind": "bridge", "name": "collect", "payload": { "entityId": "key-1" } }
    }
  ],
  "finalAssertions": [
    { "path": "player.inventory", "operator": "includes", "expected": "key-1" },
    { "path": "entities[0].collected", "operator": "equals", "expected": true }
  ]
}
```

Supported operators are `equals`, `notEquals`, `greaterThan`, `greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `includes`, and `exists`.

Use stable paths and IDs. Avoid assertions on exact frame counts, floating-point positions, or entity array order unless those details are part of the game contract. Assert invariants after the smallest action that should establish them.
