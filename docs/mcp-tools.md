# MCP tool reference

All tools return `{ ok: true, data }` or `{ ok: false, error: { code, message, hint? } }` in `structuredContent` and text form.

| Tool | Purpose | Key boundary |
|---|---|---|
| `web2d_project_inspect` | Detect package manager, frameworks, scripts, entries, and Bridge coverage | Relative paths inside `WEB2DKIT_ROOT` only |
| `web2d_session_start` | Open a controlled browser session with seed and viewport | HTTP(S) URLs; game server is already running |
| `web2d_session_stop` | Close a session and browser resources | Process-local session ID |
| `web2d_observe` | Read Bridge descriptor, state, and metrics | Requires serializable Bridge state |
| `web2d_act` | Send bounded keyboard, pointer, wait/frame, or semantic actions | No arbitrary JavaScript or shell |
| `web2d_assert` | Evaluate state-path assertions | Read-only against current state |
| `web2d_scenario_run` | Reset, check initial state, replay actions, report progress, honor client cancellation, and return exact failed steps | Maximum 500 steps and 100 assertions per scope |
| `web2d_quality_check` | Review Bridge, state, errors, resources, and render surface | Does not claim visual correctness |

## Action kinds

- `key`: key name, optional `press`/`down`/`up`, bounded delay.
- `pointer`: viewport coordinates, optional `click`/`down`/`up` and button.
- `wait`: bounded milliseconds or logical frames.
- `bridge`: named semantic action with optional JSON payload.

## Assertions

State paths support dotted properties and numeric indexes, for example `player.health` or `entities[0].state`. Operators are `equals`, `notEquals`, `greaterThan`, `greaterThanOrEqual`, `lessThan`, `lessThanOrEqual`, `includes`, and `exists`.

Assertions never evaluate JavaScript expressions.

Scenarios may define `initialAssertions`, which run after reset and before any action, plus per-step and `finalAssertions`. For Git-owned suites and CI, use the strict [Acceptance Scenario files and CLI](./scenarios.md).
