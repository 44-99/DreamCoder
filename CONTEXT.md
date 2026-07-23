# Agent-Assisted Web 2D Game Development

Web2DKit exists to help coding agents produce browser-native 2D games whose gameplay quality can be demonstrated, not merely claimed.

## Language

**Agent-Assisted Web 2D Developer**:
A developer with basic browser-development skills who uses a coding agent to create or improve a Web 2D game and wants the result to be reproducibly playable and verifiable.
_Avoid_: No-code creator, traditional engine developer, generic test engineer

**Development Quality Layer**:
The role Web2DKit plays alongside a coding agent: it guides the work from design through polish and requires reproducible evidence that the resulting gameplay loop works.
_Avoid_: Game generator, agent replacement, test framework

**Host Agent**:
The coding agent that remains responsible for generating and modifying the game while using Web2DKit's development workflow.
_Avoid_: Web2DKit agent, sub-agent

**Playable Loop**:
The smallest end-to-end player experience with working controls, rules, lifecycle, and a meaningful completion or failure outcome.
_Avoid_: Running page, visual demo, generated files

**Verified Playable Loop**:
A Playable Loop backed by at least one repeatable acceptance scenario that proves its controls, core rules, lifecycle outcomes, and restart behavior.
_Avoid_: Successful build, opened page, attractive screenshot, tool invocation count

**Activation**:
The moment an Agent-Assisted Web 2D Developer obtains a Verified Playable Loop for the first time.
_Avoid_: Installation, project generation, first page load

**Guided Development**:
Game-development work shaped by Web2DKit's workflow but not yet backed by authoritative, repeatable rule evidence.
_Avoid_: Verified development, tested game

**Game Bridge**:
The boundary through which a game makes its authoritative rule state and permitted domain actions available for verification.
_Avoid_: Debug global, renderer snapshot, arbitrary script hook

**Acceptance Scenario**:
A versioned, order-independent game-project asset that combines a reproducible starting condition, player or domain actions, and assertions proving a gameplay claim. The same scenario is reusable by the Host Agent, local developers, and CI.
_Avoid_: Prompt, one-off MCP payload, browser script, screenshot test

**Scenario Suite**:
A collection of independent Acceptance Scenarios whose aggregate result describes the rule evidence for an agreed game slice.
_Avoid_: Ordered campaign, shared-state script, Agent session history

**Native Control Evidence**:
Evidence that the controls available to a player reach the Playable Loop correctly. Every Verified Playable Loop includes at least one Acceptance Scenario with Native Control Evidence.
_Avoid_: Semantic-only coverage, programmatic state change

**Semantic Rule Evidence**:
Evidence produced through named game actions that follow the same rules as player controls while expressing complex scenarios more clearly and deterministically.
_Avoid_: Test-only shortcut, direct state mutation, arbitrary script

**Visual Review**:
A separate Host Agent assessment of layout, readability, feedback, motion, and presentation across relevant viewports. It complements Rule Evidence but cannot replace it or be inferred from it.
_Avoid_: Quality check, screenshot assertion, automated visual pass

**Game Quality Acceptance**:
Completion of both a Verified Playable Loop and its required Visual Review for the agreed game slice.
_Avoid_: Production-ready, successful build, rule-only verification

**Verified Host**:
A specific combination of coding-agent host version, operating system, and Web2DKit version whose installation, Skill discovery, tool discovery, and Acceptance Scenario workflow have been exercised and dated.
_Avoid_: MCP-compatible host, theoretically supported host

**Protocol-Compatible Host**:
A coding-agent host that implements the required open protocols but has not completed the current Web2DKit host verification workflow.
_Avoid_: Verified Host, officially supported host

**Reference Game**:
An official, reproducible game project built to test a specific unproven class of Web2DKit workflow and provide developers with executable evidence.
_Avoid_: Game template, framework endorsement, product demo only

**Framework Adapter**:
Reusable Bridge integration extracted from repeated needs across independent games without taking ownership of their authoritative state or changing the MCP vocabulary.
_Avoid_: Framework-specific MCP server, engine wrapper, example-local glue
