# Developer Audience Context

Last updated: 2026-07-23

## Product Overview

- **Product**: Web2DKit
- **One-liner**: Help developers using coding agents build, playtest, and debug browser-native 2D games with structured state and deterministic scenarios instead of relying on screenshots alone.
- **Category**: Open-source developer tool; MCP server, runtime bridge, and Agent Skills plugin.
- **Core technology**: TypeScript/Node.js, official MCP SDK, Playwright, JSON schemas, framework-neutral browser Game Bridge.
- **Supported boundary**: HTML/CSS/DOM, Canvas, SVG, Web Audio, WebGL-2D, vanilla JS/TS and lightweight 2D frameworks. No Unity, Unreal, Godot, Three.js 3D, or editor-dependent pipelines.
- **Model**: MIT licensed, local-first, no hosted account or model key.

## Developer Persona

### Primary

- Solo and small-team 2D game developers already using Codex, Claude Code, or another MCP-compatible coding agent.
- Comfortable with JavaScript/TypeScript and browser tooling; may use Phaser, PixiJS, Kaboom, Excalibur, React, Vue, or custom Canvas code.
- Wants an agent to do more than generate a prototype: reproduce gameplay bugs, verify rules, and prevent regressions.
- Personally chooses and installs development tools; no enterprise purchase is required.

### Secondary

- Game-jam participants who need fast but repeatable browser-game iteration.
- Framework maintainers and test-infrastructure contributors building reusable adapters.
- Educators teaching game loops, state models, deterministic simulation, or agent-assisted development.

Non-technical creators are not the primary audience until installation and Bridge integration require substantially less developer work.

## Where They Hang Out

- GitHub, npm, MCP and Agent Skills communities.
- Phaser, PixiJS, HTML5 game development, webdev, indie game, and game-jam Discord/Reddit communities.
- CSDN, 掘金, 知乎, 哔哩哔哩, V2EX, GitHub 中文社区.
- Search terms: `MCP game development`, `Claude Code game testing`, `Codex 2D game`, `AI game playtesting`, `Phaser automated testing`, `Canvas game testing`, `deterministic game replay`, `游戏开发 MCP`, `AI 编程 Agent 2D 游戏`.

## Problems & Pain Points

- A coding agent sees rendered pixels but cannot reliably explain the game's logical state.
- Browser automation can click coordinates but cannot prove game rules changed correctly.
- Timing and randomness make gameplay failures difficult to reproduce.
- Generated games often stop at “it runs” without control, lifecycle, win/loss, and regression verification.
- Each agent session rediscovers how to start, observe, and test the same game.
- Existing test tools require game developers to invent their own state bridge and scenario format.

## Current Alternatives

- **Generic coding agents**: strong at code changes, weak at structured gameplay observation unless the project builds custom infrastructure.
- **Playwright/Cypress scripts**: reliable browser automation, but developers must design game semantics, deterministic reset, and domain assertions themselves.
- **Screenshots or visual agents**: useful for appearance, insufficient for hidden state and rule correctness.
- **Engine-specific test systems**: useful inside their engine, outside this browser-native and cross-agent scope.
- **DIY debug globals**: quick for one project, inconsistent across projects and agent sessions.

## Key Differentiators

- Framework-neutral Game Bridge rather than a genre template or prompt collection.
- Same MCP server and Skill workflow across supported coding agents.
- Structured state, fixed seed, semantic actions, and exact failing-step assertions in one loop.
- No duplicate chat UI, LLM integration, generic file tools, arbitrary shell, database, or Docker requirement.
- Claims must be demonstrated by integration tests and real project adapters.

## Verbatim Developer Language

These are hypotheses to validate through Issues and interviews, not testimonials:

- “The agent made the game run, but it doesn't actually understand the rules.”
- “A screenshot can't tell me why the collision failed.”
- “This bug only happens sometimes after restarting the level.”
- “I don't want another game generator; I want my coding agent to test the game it wrote.”
- “How do I make Claude Code or Codex actually play a Phaser game?”

## Technical Trust Signals

- Current: MIT license, bounded MCP schemas, no arbitrary shell tool, fail-closed project root, real Chromium integration test, documented Bridge contract, explicit limitations.
- Required before stable release: three real-genre integrations, adapter conformance tests, cross-platform host installation verification, versioned prerelease, public issue feedback.
- Do not use stars, users, compatibility, or performance numbers as proof until measured.

## Conversion Actions

- **Awareness**: Understand the difference between visual inspection and game-state verification; visit the repository.
- **Consideration**: Read the scope, inspect the tool schemas and integration test, star or watch the repository.
- **Trial**: Install Chromium, start the included Bridge demo, and complete one deterministic scenario.
- **Activation**: Add the Bridge to a real game and preserve one actual bug as a passing regression scenario.
- **Community**: Submit an adapter, scenario, failure report, or developer interview finding.

## Voice & Tone

- Direct, technical, evidence-first, and respectful of existing agent capabilities.
- Lead with a reproducible developer outcome, then explain the protocol and tradeoffs.
- Avoid “AI game generator”, “one click”, “revolutionary”, “supports every framework”, or unmeasured success claims.
- Use English by default on GitHub for global discovery, with first-class Chinese README and Chinese technical content for domestic channels.

## Validation Queue

- Interview at least ten browser 2D developers using coding agents.
- Integrate one puzzle/strategy game, one action/platform game, and one narrative/simulation game.
- Measure time from clone to first observed state and from bug report to saved scenario.
- Record exact search language from Issues, CSDN comments, Reddit, Discord, and video comments.
