# Web2DKit roadmap

This roadmap is ordered by developer value and evidence, not by the number of technologies added.

## Now — prove the core loop

- [x] Standards-based MCP stdio server with bounded schemas and structured results
- [x] Framework-neutral Game Bridge v1
- [x] Fixed-seed browser sessions, native and semantic actions, state assertions, and scenarios
- [x] Real Chromium integration test
- [x] Cross-host Skill set and Codex/Claude plugin manifests
- [ ] Test local installation end to end in current Codex and Claude Code releases
- [ ] Validate the Bridge and scenario model in three real games from different genres
- [ ] Publish the first npm prerelease and Codex/Claude installation packages

## Next — real project adapters

- [ ] Phaser adapter with scene, entity, input, and fixed-step examples
- [ ] PixiJS adapter with an explicit user-owned state model
- [ ] DOM/SVG reference game outside the arcade genre
- [ ] Versioned scenario files and a CLI runner suitable for CI
- [x] Cancellation and progress reporting for long scenario runs
- [ ] Configurable performance budgets and trace artifacts

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
