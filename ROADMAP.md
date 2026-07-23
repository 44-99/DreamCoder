# Web2DKit roadmap

This roadmap is ordered by developer value and evidence, not by the number of technologies added.

## Now — prove the core loop

- [x] Standards-based MCP stdio server with bounded schemas and structured results
- [x] Framework-neutral Game Bridge v1
- [x] Fixed-seed browser sessions, native and semantic actions, state assertions, and scenarios
- [x] Real Chromium integration test
- [x] Cross-host Skill set and Codex/Claude plugin manifests
- [x] Reproducible DOM/CSS puzzle example (Signal Relay)
- [ ] Test local installation end to end in current Codex and Claude Code releases
- [x] Versioned scenario files and a bounded CLI runner suitable for CI
- [ ] Validate fixed-step scenarios in a real-time Phaser action game
- [ ] Validate long-lived state and branching in a narrative/simulation game
- [ ] Publish the first npm prerelease and Codex/Claude installation packages

## Next — evidence-based adapters

- [ ] Extract a Phaser adapter only after the action reference game reveals stable repeated glue
- [ ] PixiJS adapter with an explicit user-owned state model
- [x] Cancellation and progress reporting for long scenario runs
- [ ] Configurable performance budgets and trace artifacts

See [ADR 0002](./docs/adr/0002-keep-scenarios-declarative-and-game-owned.md) for the scenario ownership and runner boundary.

## Later — ecosystem quality

- [ ] Adapter conformance suite
- [ ] Mobile touch and gamepad scenario coverage
- [ ] Accessibility-focused game checks
- [ ] Reusable genre-specific assertion libraries without coupling the core to a genre
- [ ] Marketplace distribution and upgrade path for both primary hosts

## Non-goals

- Building another coding-agent chat interface
- Owning source editing, Git, generic browser capture, or arbitrary terminal commands
- Embedding an LLM provider or multi-agent orchestration framework
- Supporting Unity, Unreal, Godot, Three.js 3D, or editor-dependent engine pipelines
