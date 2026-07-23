# Game design contract

Keep this contract short enough to guide one implementation pass. Replace every placeholder with a decision.

## Player promise

- Target player and context:
- One-sentence fantasy:
- Target devices and inputs:
- Intended session length:

## Play loop

- Primary verbs:
- Immediate objective:
- Opposition or constraint:
- Reward and feedback:
- Failure and restart:
- Escalation or progression:
- Variety that appears within the first minute:

## Vertical slice

- First actionable screen:
- Smallest complete playable path:
- Included content:
- Explicitly deferred content:

## Presentation

- Art direction and readability rule:
- Asset strategy: sourced, generated, procedural, or mixed:
- Camera and world framing:
- HUD/menu hierarchy:
- Audio and motion priorities:
- Desktop/mobile and accessibility expectations:

## Observable state contract

Expose only stable, rule-relevant JSON facts:

```text
scene/lifecycle
player state and capabilities
rule-relevant entities with stable IDs
objective, score, timer, turn, or progression state
pause/focus/input state when it affects rules
win/loss/restart state
```

For each semantic action, record its name, payload, preconditions, and state transition. Native input and semantic dispatch must reach the same authoritative rule path.

## Acceptance scenarios

For each claim, specify:

```text
Given: seed and observable initial state
When: shortest player action sequence
Then: state paths and expected values
Visual review: only the appearance questions that screenshots must answer
```

Include at least one complete loop, one failure/restart path, and one lifecycle or input-boundary check when relevant.
