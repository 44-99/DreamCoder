# Game production quality

## Complete-loop gate

A mechanic becomes a game slice when it has:

- a clear first action and objective;
- opposition, scarcity, uncertainty, time pressure, or another constraint;
- visible consequences and readable state changes;
- success or failure with a restart path;
- at least one escalation, choice, or variation;
- enough feedback that important actions feel distinct.

Prefer two well-developed quality layers over a broad list of unfinished systems.

## Asset plan

Create a manifest before implementation hardens around placeholder dimensions:

```text
asset key | gameplay role | source | dimensions/anchor | animation/audio states | fallback
```

Use sourced or generated art for recognizable player-facing content when visual identity matters. Procedural shapes are valid for intentionally abstract games, prototypes explicitly requested as such, collision/debug overlays, particles, and transient feedback. Do not present accidental programmer art as a finished visual direction.

For sprite animation, approve one identity frame, generate or author related frames as a coherent set, normalize shared scale and anchor, preview at in-game size, and verify collisions after normalization.

## UI and feel

- Put critical status nearest the relevant action; hide secondary detail behind menus.
- Keep the central playfield clear and make input focus explicit under overlays.
- Reserve strong motion, hit stop, shake, particles, and audio for meaningful events.
- Support pause/focus loss, restart, resize, and the promised input modes.
- Respect reduced motion and provide keyboard-visible focus when DOM controls are used.

## Evidence split

| Claim | Evidence |
|---|---|
| Rule, score, collision, inventory, lifecycle | structured Bridge state and assertions |
| Control wiring | native key/pointer actions plus state change |
| Composition, readability, animation, HUD obstruction | browser screenshot or video review |
| Startup, exceptions, failed resources | `web2d_quality_check` and host logs |

Do not substitute one evidence type for another.
