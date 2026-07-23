# Security boundaries

Web2DKit treats game pages and project contents as untrusted local inputs.

- Project inspection is fail-closed to `WEB2DKIT_ROOT`, the first MCP file root, or the server working directory (in that order), and rejects absolute paths, parent traversal, and resolved symlink escapes.
- The inspector skips dependency, build, cache, and Git directories and caps file discovery.
- Browser sessions accept only `http://` and `https://` URLs. They do not execute user-provided shell commands or arbitrary JavaScript snippets.
- MCP arguments have explicit schemas, numeric bounds, action limits, and scenario limits.
- Bridge actions are named JSON messages; the bridge must not map them to `eval`, shell, or unrestricted module loading.
- Tool failures return stable error codes and do not silently fall back to unsafe local operations.
- Sessions and diagnostics are memory-only in v0.1. Web2DKit has no database, account system, analytics, or model credentials.

The browser can still reach the URL supplied by the caller. Run untrusted games with appropriate network and OS isolation. Web2DKit's checks are not a malware sandbox or security audit.

Report vulnerabilities through GitHub Private Vulnerability Reporting rather than a public issue.
