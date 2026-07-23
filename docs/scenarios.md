# Acceptance scenarios and CLI

Acceptance Scenarios are versioned game-project assets. They prove gameplay rules against the same Game Bridge used by the MCP tools, without embedding JavaScript or starting arbitrary server commands.

## File convention

Store one scenario per `*.web2d.json` file. A conventional location is `web2dkit/scenarios/`:

```json
{
  "schemaVersion": "1",
  "name": "restart returns to a ready state",
  "seed": 42,
  "initialAssertions": [
    { "path": "lifecycle.status", "operator": "equals", "expected": "ready" }
  ],
  "steps": [
    {
      "action": { "kind": "key", "key": "Enter" },
      "assertions": [
        { "path": "lifecycle.status", "operator": "equals", "expected": "playing" }
      ]
    }
  ],
  "finalAssertions": [
    { "path": "lifecycle.status", "operator": "equals", "expected": "playing" }
  ]
}
```

The v1 schema is strict: unknown fields are rejected, there is no executable-code field, and every action uses the same bounded action vocabulary as `web2d_act`. `initialAssertions` run immediately after the scenario reset and before the first action.

## Run a suite

Start the game with its own development or preview command. Then point the built CLI at its HTTP(S) URL:

```bash
web2dkit run --url http://127.0.0.1:4173 web2dkit/scenarios
web2dkit run --url http://127.0.0.1:4173 --reporter json web2dkit/scenarios
```

When developing from this repository, replace `web2dkit` with `node /absolute/path/to/Web2DKit/dist/cli.js`.

The runner recursively loads scenario files in stable path order, resets before every scenario, continues after failures, and reports the complete suite. It exits with code `1` if any scenario fails. Scenarios must be independent and must not rely on execution order.

## Evidence boundary

A Verified Playable Loop needs both:

- at least one native-input scenario for the real player control path;
- semantic Bridge scenarios for exact rule assertions, using the same domain-rule path as native input.

Scenario success proves structured behavior, not visual excellence. Use the host Agent's browser and screenshot workflow for a separate Visual Review.

See the executable files in [Signal Relay](../examples/signal-relay/web2dkit/scenarios/) and the ownership rationale in [ADR 0002](./adr/0002-keep-scenarios-declarative-and-game-owned.md).
