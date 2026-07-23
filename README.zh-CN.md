<p align="right">
  <a href="./README.md">English</a> · <strong>简体中文</strong>
</p>

<div align="center">
  <img src="./docs/assets/web2dkit-logo.svg" alt="Web2DKit logo" width="96" />
  <h1>Web2DKit</h1>
  <p><strong>面向浏览器原生 2D 游戏的 MCP 工具与 Agent Skills。</strong></p>
  <p>让 Codex、Claude Code 等编程 Agent 真正理解、试玩和验证游戏，而不是再套一层提示词。</p>

  [![CI](https://github.com/44-99/Web2DKit/actions/workflows/ci.yml/badge.svg)](https://github.com/44-99/Web2DKit/actions/workflows/ci.yml)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
  [![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933.svg?logo=node.js&logoColor=white)](https://nodejs.org/)
</div>

## 为什么需要 Web2DKit？

编程 Agent 已经能写代码、改文件、运行命令和查看截图，但它通常不知道：当前处于哪个场景、一次碰撞是否正确扣血、哪一步破坏了规则、相同输入能否稳定复现问题。

Web2DKit 通过小型 Game Bridge 和受限 MCP 工具补上“游戏语义层”：

```text
需求 → 编程 Agent → 修改源码
                    ↓
           Web2DKit Skill 工作流
                    ↓
固定 seed → 执行动作 → 读取结构化状态 → 规则断言 → 回归场景
```

## 当前已经能做什么

- 在配置的项目根目录内识别 Web 2D 技术栈、入口、脚本和 Bridge 覆盖情况。
- 使用固定随机种子启动受控 Playwright 游戏会话。
- 通过 Game Bridge 读取场景、实体、规则、得分和指标等 JSON 状态。
- 执行受限的键盘、指针、等待/逻辑帧和语义动作。
- 运行包含逐步断言与最终断言的确定性场景。
- 检查运行时异常、资源加载失败、Bridge 状态和渲染/交互表面。
- 提供开发、试玩、调试三个可执行 Skill 工作流。
- 使用同一仓库适配 Codex 与 Claude Code 插件格式。

Web2DKit 不负责聊天记录、模型路由、任意 shell、通用文件编辑或新的 Web IDE，这些能力应继续由宿主 Agent 负责。

## 项目边界

支持 HTML/CSS/DOM、Canvas 2D、SVG、Web Audio、WebGL 2D，以及原生 JavaScript/TypeScript、Phaser、PixiJS、Kaboom、Excalibur 等浏览器原生 2D 技术路线。

Unity WebGL、Unreal Engine、Godot、Three.js 3D 场景和依赖重量级编辑器的工作流不在范围内。

v0.1 已实现框架无关 Bridge。当前能识别常见技术栈，但 Phaser、PixiJS 的深度适配仍在 Roadmap 中，不会提前宣称完成。

## 本地验证

需要 Node.js 22+：

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

这会运行单元测试，以及基于真实 Chromium 和内置 [Bridge 示例](./examples/bridge-demo/)的完整状态—动作—断言测试。

插件本地安装与首次使用见[入门指南](./docs/getting-started.zh-CN.md)。

## 一分钟接入 Game Bridge

将游戏已有的权威状态暴露出来：

```js
window.__WEB2D_GAME__ = {
  describe: () => ({ protocolVersion: "1", name: "my-game" }),
  getState: () => structuredClone(gameState),
  reset: ({ seed } = {}) => resetGame(seed ?? 1),
  dispatch: ({ name, payload }) => dispatchGameAction(name, payload)
};
```

Agent 随后可以通过 `web2d_session_start` → `web2d_observe` → `web2d_scenario_run` 证明游戏规则，而不是只看截图猜测结果。

## 文档

- [中文入门指南](./docs/getting-started.zh-CN.md)
- [Architecture](./docs/architecture.md)
- [Game Bridge protocol](./docs/bridge-protocol.md)
- [MCP tools](./docs/mcp-tools.md)
- [Security boundaries](./docs/security.md)
- [Roadmap](./ROADMAP.md)
- [参与贡献](./CONTRIBUTING.md)

## 当前状态

Web2DKit 目前是可以运行和测试的早期基础版本。浏览器集成测试已经证明核心闭环，但在稳定发布前仍需要真实项目适配器、场景文件持久化、性能预算以及 2D 游戏开发者反馈。

Web2DKit 使用 [MIT License](./LICENSE)。
