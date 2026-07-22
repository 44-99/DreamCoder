# DreamCoder example gallery

这些示例是为文档、视觉验证和首次体验人工整理的确定性样例，不代表特定模型或 provider 的固定输出质量。

These deterministic examples are curated for documentation, visual QA, and first-use exploration. They do not claim a fixed output quality for any model or provider.

## Run locally

直接打开 `examples/index.html`，或在仓库根目录启动静态服务器：

```bash
python -m http.server 4173
```

然后访问 <http://localhost:4173/examples/>。

| Game | Controls | Entry |
|---|---|---|
| Neon Snake | Arrow keys / WASD / Space | `neon-snake/index.html` |
| Prism Breakout | Mouse / Arrow keys / A-D | `prism-breakout/index.html` |
| Orbit Dodge | Arrow keys / WASD | `orbit-dodge/index.html` |

每个游戏都是不依赖外部资源的单文件 HTML/CSS/JavaScript 页面，可作为 DreamCoder 生成产物的格式参考。
