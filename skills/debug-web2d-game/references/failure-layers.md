# Failure layers

Classify the first incorrect transition before editing:

| Layer | Evidence | Typical owners |
|---|---|---|
| Startup and loading | page or request error before playable state | dev server, entry point, asset URL, initialization |
| Input | native action absent while domain dispatch works | focus, event listener, key mapping, pointer scaling |
| State and rules | structured state changes incorrectly | reducer, game system, collision resolution, turn rules |
| Time and determinism | same seed/action sequence diverges | wall clock, randomness, async order, frame delta |
| Lifecycle | restart or scene change retains old behavior | timers, subscriptions, entity teardown, global state |
| Rendering | state is correct but display is wrong | transforms, camera, sprite mapping, z-order, CSS |
| Performance | rules are correct but deadlines are missed | allocation, entity count, draw calls, long tasks |

Collect evidence on both sides of the suspected boundary. Compare native input with bridge dispatch before changing movement rules, and compare `getState()` with the rendered scene before changing the renderer.
