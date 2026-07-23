# Visual playtest checklist

Capture only states that answer a concrete question.

## First playable screen

- Is the objective and primary action discoverable without a wall of instructions?
- Does the screen look like a game rather than an admin dashboard or engine demo?
- Are loading, start, focus, and audio-unlock states clear?

## During play

- Do player, hazards, goals, pickups, projectiles, tiles, and hit areas read at game scale?
- Are sprite baselines, anchors, facing, animation timing, and collisions visually coherent?
- Do important actions have distinct visual or audio feedback without obscuring play?
- Does the camera preserve orientation and avoid unwanted sub-pixel blur for pixel art?
- Does the HUD protect the central playfield and update without flicker?

## Lifecycle and overlays

- Do pause, menu, dialog, win, loss, and restart surfaces communicate current state?
- Is gameplay input gated while a modal owns focus?
- After restart, are stale sprites, particles, timers, prompts, or duplicate HUD elements absent?

## Responsive and accessible behavior

- Check the promised desktop and mobile viewports, not arbitrary device coverage.
- Verify safe areas, touch target size, orientation changes, and canvas scaling where relevant.
- Check keyboard focus, contrast, readable text, reduced-motion behavior, and non-color-only state cues.

Record viewport, state/setup, visible defect, severity, and likely owner: simulation, renderer, UI, asset, or lifecycle.
