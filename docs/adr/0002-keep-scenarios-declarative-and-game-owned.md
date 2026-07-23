# Keep acceptance scenarios declarative and game-owned

Acceptance Scenarios are strict, versioned assets stored with the game project and executed by the same bounded core through MCP or CLI. Web2DKit connects only to an explicitly supplied HTTP(S) game URL and does not execute project server commands. This trades one-command process orchestration for a stable security boundary, cross-platform behavior, and scenarios that developers can review, replay locally, and run in CI without an Agent.
