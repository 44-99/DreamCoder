# Windows host development verification — 2026-07-23

This record distinguishes manifest discovery, MCP health, and an Agent-executed workflow. A host is not considered verified until all required gates pass.

## Environment

- Windows 11, PowerShell 7
- Node.js 22+
- Web2DKit source commit baseline: `3674fd0`
- Signal Relay workspace example

## Codex CLI 0.145.0-alpha.30

### Passed

- Codex plugin validation passed.
- A temporary local marketplace installed and enabled Web2DKit `0.1.0`.
- A fresh Codex task discovered all five Web2DKit Skills.
- The current Codex alpha did not resolve `${PLUGIN_ROOT}` or relative stdio script arguments from plugin MCP metadata. Registering the built server with an explicit absolute path succeeded.
- A fresh read-only Codex task called `web2d_project_inspect` against Signal Relay and observed `packageManager: npm`, five source files, and Bridge coverage in `src/main.ts`.

### Remaining gate

Non-interactive `codex exec` cancelled `web2d_session_start` because the tool requires interactive approval. Project inspection passed, but session start, observation, assertion, quality check, and cleanup were not counted as host-level success. The same MCP server's complete Signal Relay flow passes through the repository acceptance runner.

### Development configuration used

```powershell
codex mcp add web2dkit -- node C:\absolute\path\to\Web2DKit\dist\server.js
```

The Codex plugin supplies Skills in this development setup; the explicit MCP registration supplies runtime tools. An all-in-one installed package remains a distribution-stage gate.

## Claude Code 2.1.202

### Passed

- `claude plugin validate --strict` passed.
- `claude --plugin-dir ... plugin details web2dkit` discovered five Skills and one MCP server.
- `claude --plugin-dir ... mcp list` reported `plugin:web2dkit:web2dkit` connected to the built server.

### Remaining gate

A no-plugin baseline `claude -p` request and the Web2DKit verification request both produced no model output within the bounded test window. Authentication was valid, so no Agent-executed project inspection or Signal Relay scenario was claimed. This is recorded as a host/runtime response blocker, not a plugin pass or plugin failure.

## Shared core evidence

The repository acceptance runner independently starts Signal Relay, launches the same built stdio server, lists eight MCP tools, verifies seed 42, native input, deterministic repeated victory, pause behavior, runtime diagnostics, and cleanup.

## Status

Neither host is yet labeled a Verified Host. Codex needs one approved interactive browser-session run; Claude Code needs a responsive model session that executes the connected tool. Ubuntu CI continues to cover the host-neutral MCP core.
