# Stack selection

Choose from product constraints and the existing repository, not popularity.

| Stack | Prefer when | Avoid when |
|---|---|---|
| DOM/CSS/SVG | Cards, boards, puzzles, narrative, management, accessibility-heavy UI | Large animated worlds or many sprites |
| Canvas 2D | Small custom loops, drawing-heavy games, minimal dependencies | You need mature scenes, tilemaps, cameras, or physics quickly |
| Phaser | Arcade, platformer, top-down, tilemap, tactics, sprite animation, common 2D game primitives | The game is mostly document UI or needs a highly custom renderer |
| PixiJS | Sprite-heavy rendering, custom simulation, particles, bespoke scene composition | You expect a full game framework, physics, or scene lifecycle out of the box |
| Existing framework | The repository already has working conventions and tooling | Only when a measured requirement cannot be met |

Use TypeScript and Vite for a new modular project when they reduce integration risk; do not migrate an existing JavaScript game only to match this preference.

## Sizing the architecture

- Jam/small game: a few scenes or modes, explicit state module, action map, asset manifest, Bridge adapter.
- Mid-size game: simulation systems, content data, renderer adapters, UI layer, lifecycle ownership, scenario fixtures.
- Content-heavy game: data validation, streaming/loading boundaries, save migrations, performance budgets, adapter conformance.

Do not introduce ECS, global event buses, state libraries, or physics engines until the actual entity count, coordination, or collision requirements justify them.
