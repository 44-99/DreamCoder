# Contributing to Web2DKit / 参与贡献

High-value contributions make a real Web 2D workflow more observable, deterministic, or reproducible. Useful examples include a framework adapter backed by a sample game, a saved regression scenario, a lifecycle bug reproduction, or a clearer failure message.

高价值贡献应当让真实 Web 2D 工作流更容易观测、确定性复现或验证，例如带示例项目的框架适配器、回归场景、生命周期缺陷复现或更清晰的错误信息。

## Before you start

- Open an Issue for design changes and describe the developer problem before proposing a dependency.
- Keep the core browser-native and host-neutral. Do not add model providers, chat UI, arbitrary shell tools, databases, or 3D engine workflows.
- Report vulnerabilities privately and remove tokens, personal data, and proprietary game assets from reproductions.

## Local development

Requires Node.js 22+:

```bash
npm ci
npx playwright install chromium
npm run validate
```

The validation command type-checks, runs unit and Chromium integration tests, and builds the MCP server.

Validate plugin and Skill metadata before submitting:

```bash
python /path/to/plugin-creator/scripts/validate_plugin.py .
python /path/to/skill-creator/scripts/quick_validate.py skills/build-web2d-game
python /path/to/skill-creator/scripts/quick_validate.py skills/playtest-web2d-game
python /path/to/skill-creator/scripts/quick_validate.py skills/debug-web2d-game
```

## Pull requests

1. Keep one user problem per PR.
2. Add a failing test or reproducible scenario before changing behavior when practical.
3. Preserve MCP input bounds and the `WEB2DKIT_ROOT` boundary.
4. Document protocol changes and keep v1 additions backward-compatible.
5. Report the exact commands and real-browser checks you ran.

Good first issues include additional project-stack detection, Bridge examples for different game genres, assertion error improvements, cross-platform installation checks, and framework adapter design backed by a minimal working game.

Contributions are licensed under the project's [MIT License](./LICENSE).
