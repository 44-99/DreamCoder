# Contributing to DreamCoder / 参与贡献

感谢你愿意改进 DreamCoder。最有价值的贡献是可复现的生成失败、可玩的示例游戏、provider 兼容性修复、安全改进和跨平台 Quickstart 反馈。

Thanks for contributing. High-value contributions include reproducible generation failures, playable examples, provider compatibility fixes, security improvements, and cross-platform quickstart feedback.

## 开始之前 / Before you start

- Bug 或设计建议请先创建 Issue，说明用户问题和复现条件。
- 安全漏洞请使用 GitHub Private Vulnerability Reporting，不要公开披露。
- 不要在 Issue、日志、截图或测试中提交 API Key、Token 或个人信息。

Open an issue for bugs or design proposals. Report vulnerabilities privately, and never include API keys, tokens, or personal data in issues, logs, screenshots, or tests.

## 本地开发 / Local development

环境要求：Python 3.11+、Node.js 20.19+ 或 22.12+。

```bash
git clone https://github.com/44-99/DreamCoder.git
cd DreamCoder
```

后端：

```bash
cd backend
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

前端：

```bash
cd frontend
npm ci
npm run build
```

代码检查：

```bash
ruff check backend
```

## Pull Request

1. 每个 PR 只解决一个清晰问题。
2. 行为变化必须补测试；UI 变化必须附截图。
3. 不要顺便格式化或重构无关文件。
4. 确保 CI 通过，并在 PR 中说明实际验证命令。
5. 提交信息建议使用 `feat:`、`fix:`、`docs:`、`test:`、`refactor:` 或 `chore:` 前缀。

Keep each PR focused, add tests for behavior changes, include screenshots for UI changes, avoid unrelated rewrites, and report the commands you actually ran.

## Good first contributions

- 为现有 provider 增加不调用真实 API 的配置测试；
- 提交一个单文件 HTML/CSS/JavaScript 示例游戏；
- 补充 Windows、macOS 或 Linux 的安装故障排查；
- 改进错误提示、无障碍标签或文档链接。

提交 PR 即表示你同意按项目的 [MIT License](./LICENSE) 授权你的贡献。
