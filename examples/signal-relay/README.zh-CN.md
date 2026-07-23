# Signal Relay：可复现的端到端案例

[English](./README.md)

Signal Relay 是一个使用 Web2DKit 的设计、构建、试玩和打磨 Skills 从零制作的确定性网格解谜游戏。它同时是一份可执行证据：真实 MCP Server 能检查项目、初始化 Game Bridge、执行原生输入与语义动作、重复场景并验证游戏规则。

| 项目 | 内容 |
|---|---|
| 用时 | 5–10 分钟 |
| 环境 | Node.js 22+、通过 Playwright 安装 Chromium |
| 技术栈 | TypeScript、DOM/CSS、Vite、Vitest |
| 目标 | 依次激活 A → B → C，然后到达上行节点 |

## 一条命令完成验收

在 Web2DKit 仓库根目录运行：

```bash
npm ci
npx playwright install chromium
npm run example:signal-relay:e2e
```

命令会构建 Web2DKit、在可用本地端口启动游戏、通过 stdio 启动真实 MCP Server、执行全部场景、输出精简 JSON 结果，并自动关闭进程。

预期结果：

```json
{
  "ok": true,
  "tools": 8,
  "seed": 42,
  "nativeInput": true,
  "deterministicReplay": true,
  "winningScore": 570,
  "qualityCheck": true
}
```

## 手动试玩

```bash
npm run example:signal-relay:dev
```

打开 Vite 输出的地址。方向键或 WASD 移动，Escape 暂停，R 重新开始；窄屏下会显示触控方向键。

## 案例如何证明 Web2DKit 有效

1. [`docs/game-contract.md`](./docs/game-contract.md) 在编码前明确玩家体验、核心循环、范围、表现和验收场景。
2. [`src/domain.ts`](./src/domain.ts) 将确定性规则与渲染分离。
3. [`src/main.ts`](./src/main.ts) 渲染游戏并暴露 `window.__WEB2D_GAME__`。
4. [`tests/domain.test.ts`](./tests/domain.test.ts) 在不启动浏览器时验证规则。
5. [`scripts/run-web2dkit-acceptance.mjs`](./scripts/run-web2dkit-acceptance.mjs) 使用构建后的 Web2DKit MCP Server 对真实运行游戏做端到端验收。

MCP 断言负责证明结构化状态和规则；外观仍由宿主 Agent 的浏览器单独检查，因为截图和语义状态解决的是两类问题。

## 常见问题

### 没有安装 Chromium

```bash
npx playwright install chromium
```

### 找不到 `dist/server.js`

请使用根目录命令 `npm run example:signal-relay:e2e`，它会先构建 Web2DKit。

### 场景失败

先查看输出中的失败步骤与断言，再运行 `npm run example:signal-relay:dev` 做视觉检查。不要用截图替代失败的规则断言。
