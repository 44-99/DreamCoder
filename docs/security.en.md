# DreamCoder security boundaries

DreamCoder displays and executes model-generated HTML/CSS/JavaScript. Generated content must be treated as untrusted input, not as an ordinary template.

## Protections implemented today

- The Generated Artifact module rejects absolute paths, `..` traversal, excessive file counts, and oversized content.
- Only a file set that passes one validation path can enter the static project directory.
- Files are written to a temporary directory before an atomic target replacement.
- The frontend injects a CSP and uses the minimal `iframe sandbox="allow-scripts"` setting.
- The default CSP blocks network connections, form submission, top navigation, plugin objects, and remote resources.
- API keys are read only from backend environment variables and must never enter the frontend bundle, issues, logs, or screenshots.

Relevant implementation:

- `backend/modules/generated_artifact.py`
- `frontend/src/utils/htmlGenerator.js`
- `frontend/src/views/GameChatView.vue`

## What these protections do not mean

The current controls are not a complete sandbox or a security audit. In particular:

- previews are still served from the same site as the main application;
- browsers and CSP implementations may contain unknown bypasses;
- generated-code validation focuses on paths and heuristics, not proof of application safety;
- adversarial multi-tenant use has not received an independent penetration test.

Do not expose this version as a public arbitrary-code runner for anonymous internet users.

## Local development versus public hosting

| Area | Local default | Public-hosting requirement |
|---|---|---|
| Verification delivery | Console development code | `AUTH_DELIVERY_MODE=external` with SMTP/SMS |
| JWT secret | Example value | High-entropy, unique, secret-managed `SECRET_KEY` |
| Database | SQLite | PostgreSQL when concurrency and backup needs justify it |
| Verification state | In process | Redis for multiple instances |
| CORS | Local frontend origins only | Set the real frontend origin with `CORS_ALLOWED_ORIGINS` |
| Preview | Same-site static path | Separate origin or disposable isolated container |
| TLS | None | HTTPS and security response headers |

## Secret handling

- Put real keys only in untracked `backend/.env` files or the deployment platform's secret store.
- Run `git diff --cached` before committing and check for credentials, databases, and personal data.
- If a key entered Git history, revoke it at the provider immediately; deleting it from the latest file is insufficient.
- Remove authorization headers, tokens, phone numbers, email addresses, and sensitive model output from logs and bug reports.

## Reporting a vulnerability

Prefer GitHub Private Vulnerability Reporting. Public issues should not contain directly exploitable details or real credentials.

## Security roadmap

1. move previews to a separate origin or isolated container;
2. add strict startup validation for production configuration;
3. add browser-level malicious-example regression tests;
4. commission an independent review before supporting public multi-tenant use.
