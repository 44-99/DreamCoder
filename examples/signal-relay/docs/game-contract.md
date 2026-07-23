# Signal Relay game contract

## Player promise

- Target: keyboard/touch browser players who enjoy five-minute deterministic puzzles.
- Fantasy: route a courier through a failing signal grid and restore its relay chain.
- Inputs: arrows/WASD, touch direction buttons, Escape pause, R restart.
- Session: two to five minutes.

## Play loop

- Move one grid cell per action; every valid move costs one energy.
- Activate A, B, and C in order, then reach the uplink.
- Static interference cells cost two additional energy; one seeded charge restores energy.
- Win by transmitting before energy reaches zero; lose on depletion; restart preserves the seed.
- Score rewards relays, charge collection, completion, and remaining energy.

## Vertical slice

- Includes ready, playing, paused, won, lost, and restart states.
- Includes one complete board, deterministic seed variation, keyboard and touch inputs, responsive layout, and reduced-motion support.
- Defers audio, multiple levels, saved progression, authored sprite assets, and gamepad input.

## Presentation

- Intentional abstract tactical-terminal art; entities use a consistent geometric language rather than temporary programmer art.
- DOM/CSS grid keeps text, focus, touch controls, and responsiveness native to the browser.
- HUD stays outside the playfield; overlays gate start, pause, win, and loss.

## Acceptance scenarios

1. Start through native Enter, move right, and observe position/energy change.
2. With seed 42, activate A → B → C and reach the uplink; assert won and score >= 500.
3. Pause, attempt movement, and assert position does not change; resume and move.
4. Restart with the same seed and assert the initial state and charge identity are stable.
