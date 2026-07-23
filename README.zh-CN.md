<p align="center">
  <a href="./README.md">English</a> · <a href="./README.zh-CN.md"><strong>简体中文</strong></a>
</p>

<div align="center">
  <img src="./docs/assets/web2dkit-logo.svg" alt="Web2DKit 标志" width="112" />
  <h1>Web2DKit</h1>
  <p><strong>面向编程 Agent 的 2D 游戏开发能力层。</strong></p>
  <p>帮助 Codex、Claude Code 等编程 Agent 更高质量、更高效率地制作浏览器原生 2D 游戏——从明确玩法，到可重复试玩与验证。</p>

  <a href="https://github.com/44-99/Web2DKit/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/44-99/Web2DKit/ci.yml?branch=main&style=flat-square&label=CI" alt="CI 状态" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-0f766e?style=flat-square" alt="MIT 许可证" /></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-22%2B-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node.js 22 或更高版本" /></a>
  <img src="https://img.shields.io/badge/MCP-compatible-7c3aed?style=flat-square" alt="兼容 MCP" />
  <img src="https://img.shields.io/badge/Agent_Skills-included-2563eb?style=flat-square" alt="包含 Agent Skills" />
  <a href="https://github.com/44-99/Web2DKit/stargazers"><img src="https://img.shields.io/github/stars/44-99/Web2DKit?style=flat-square" alt="GitHub Stars" /></a>

  <p>
    <a href="#快速开始">快速开始</a> ·
    <a href="#skill-工作流">Skills</a> ·
    <a href="./docs/mcp-tools.md">MCP 工具</a> ·
    <a href="./docs/bridge-protocol.md">Game Bridge</a> ·
    <a href="./ROADMAP.md">Roadmap</a>
  </p>
</div>

---

## 为什么需要 Web2DKit？

编程 Agent 已经能够写代码、运行终端和查看截图，但截图无法证明一次碰撞是否正确扣血、一个谜题是否进入合法状态，或重开关卡后是否清除了所有计时器。

Web2DKit 补上缺失的游戏开发反馈闭环：

| 仅使用编程 Agent | 编程 Agent + Web2DKit |
|---|---|
| 根据提示生成若干机制 | 先明确玩家循环、垂直切片和质量标准 |
| 从画面猜测隐藏状态 | 读取场景、实体、目标和生命周期等结构化状态 |
| 点击坐标并依赖等待 | 使用受限的原生输入和游戏语义动作 |
| 页面能运行就结束 | 通过固定种子和显式断言证明游戏规则 |
| 下一次会话重新摸索流程 | 通过 Skills 重放短小的回归场景 |

```text
游戏想法 → 设计 Skill → 编程 Agent 修改游戏
                              ↓
视觉检查 ← Game Bridge ← MCP 动作、观察和断言
    └────────────────── 继续迭代 ──────────────────┘
```

Web2DKit 不替代编程 Agent、浏览器、终端或渲染器，而是让它们使用同一套可测试的 2D 游戏规则语言。

## 项目包含什么

- **5 个游戏开发 Skill**：设计、开发、试玩、调试和打磨。
- **8 个受限 MCP 工具**：项目检查、浏览器会话、状态观察、动作、断言、场景运行和运行时质量检查。
- **框架无关的 Game Bridge**：暴露权威 JSON 状态，不泄漏渲染器对象，也不允许任意 JavaScript 执行。
- **版本化验收场景与受限 CLI**：为本地和 CI 提供可重复的规则验证。
- **Codex 与 Claude Code 插件清单**：共用同一个本地 Node.js MCP Server。

## Skill 工作流

| Skill | 适用场景 | MCP 证据 |
|---|---|---|
| `design-web2d-game` | 将模糊想法整理为玩家循环、垂直切片、状态契约和验收场景 | 项目检查和可验证的游戏设计 |
| `build-web2d-game` | 开发或扩展 Canvas、DOM/SVG、Phaser、PixiJS 等 Web 2D 游戏 | 观察初始状态并断言完整循环 |
| `playtest-web2d-game` | 验证控制、规则、生命周期、响应式 UI 和回归问题 | 确定性场景与独立视觉检查 |
| `debug-web2d-game` | 定位第一个错误状态变化，而不是只修补表面现象 | 固定种子复现和回归断言 |
| `polish-web2d-game` | 在不破坏规则的前提下改善手感、UI、美术、无障碍或性能 | 前后视觉证据与场景保护 |

这些 Skill 会严格区分“游戏规则证据”和“视觉质量证据”。Web2DKit 负责结构化游戏语义；截图和页面视觉检查继续使用宿主 Agent 已有的浏览器能力。

## 快速开始

需要 Node.js 22+：

```bash
git clone https://github.com/44-99/Web2DKit.git
cd Web2DKit
npm ci
npx playwright install chromium
npm run validate
```

随后按照[中文入门指南](./docs/getting-started.zh-CN.md)，在 Codex 或 Claude Code 中加载本地插件，并连接到一个正在运行的 Web 2D 游戏。

如果希望查看完整证据而不是最小演示，可以运行官方的 [Signal Relay 端到端案例](./examples/signal-relay/README.zh-CN.md)：

```bash
npm run example:signal-relay:e2e
```

它会自动启动游戏，并使用真实 MCP Server 验证原生输入、seed 传递、确定性重放、暂停逻辑、获胜路线与运行时质量。

可以尝试这些提示：

```text
使用 $design-web2d-game 把这个益智游戏想法整理成一个可测试的游戏契约。
使用 $build-web2d-game 实现第一个完整玩家循环并验证它。
使用 $playtest-web2d-game 证明重新开始后棋盘和得分被正确重置。
```

## 60 秒接入 Game Bridge

暴露游戏本身已经拥有的可序列化权威状态：

```js
window.__WEB2D_GAME__ = {
  describe: () => ({ protocolVersion: "1", name: "my-game" }),
  getState: () => structuredClone(gameState),
  reset: ({ seed } = {}) => resetGame(seed ?? 1),
  dispatch: ({ name, payload }) => dispatchGameAction(name, payload)
};
```

Agent 随后可以执行 `web2d_session_start` → `web2d_observe` → `web2d_scenario_run`，用状态和断言证明游戏行为，而不是根据画面猜测。详见 [Bridge 协议](./docs/bridge-protocol.md)和 [MCP 工具参考](./docs/mcp-tools.md)。

## 项目边界

Web2DKit 面向使用 DOM/CSS、Canvas 2D、SVG、Web Audio 或 WebGL 2D 渲染器构建的浏览器原生 2D 游戏，适用于原生 JavaScript/TypeScript，以及 Phaser、PixiJS、Excalibur、Kaboom 等框架。

Unity、Unreal、Godot、Three.js 3D 场景和依赖编辑器的工作流不在当前范围内。目前已经支持框架识别；Phaser 与 PixiJS 的深度适配仍属于 Roadmap，不会提前宣称完成。

## 文档

- [中文入门指南](./docs/getting-started.zh-CN.md)
- [Signal Relay 端到端案例](./examples/signal-relay/README.zh-CN.md)
- [Architecture](./docs/architecture.md)
- [Game Bridge protocol](./docs/bridge-protocol.md)
- [验收场景与 CLI](./docs/scenarios.md)
- [MCP tool reference](./docs/mcp-tools.md)
- [领域语言](./CONTEXT.md)
- [为什么 Web2DKit 只增强宿主 Agent](./docs/adr/0001-augment-the-host-agent.md)
- [为什么场景是游戏项目资产](./docs/adr/0002-keep-scenarios-declarative-and-game-owned.md)
- [最新 Windows 主机验收记录](./docs/verification/2026-07-23-windows-host-development.md)
- [Security boundaries](./docs/security.md)
- [Roadmap](./ROADMAP.md)
- [参与贡献](./CONTRIBUTING.md)

## 当前状态

Web2DKit 目前是可运行的早期基础版本。真实 Chromium 集成测试与 Signal Relay 益智游戏案例已经证明“状态 → 动作 → 断言”闭环；动作和模拟类案例仍是稳定发布前的可信度门槛。

项目采用 MIT 许可证，面向希望编程 Agent 不仅能生成游戏，还能理解、试玩和验证游戏的开发者。
