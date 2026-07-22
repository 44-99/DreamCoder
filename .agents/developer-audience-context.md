# Developer Audience Context

Last updated: 2026-07-23

## Product Overview

- **Product**: DreamCoder
- **Repository positioning**: 面向 AI 应用开发者与学习者的开源、自托管 Web 游戏生成工作台和参考实现。
- **One-liner**: 用自然语言生成、继续修改并预览可运行的 HTML/CSS/JavaScript 小游戏，同时展示一个完整 AI 应用如何组织工作流、项目状态和生成产物。
- **Category**: 开源 AI 应用、开发者示例项目、自托管 Web 应用；当前不是成熟 SaaS，也不是通用 AI IDE。
- **Core technology**: Python/FastAPI、Vue 3、LLM provider、可选 LangGraph、SQLAlchemy。
- **Model**: MIT 开源项目；用户自行提供模型凭据。

## Developer Persona

### Primary

- 中国开发者社区中的初级到中级全栈、Python 或 AI 应用开发者。
- 正在学习 LLM 应用工程，希望看到比聊天机器人更完整、但仍可理解和改造的项目。
- 常用 Python、Vue/JavaScript、FastAPI，对 LangChain/LangGraph、Agent、结构化输出、SSE 和生成式 UI 感兴趣。
- 可能是个人开发者、学生、求职作品集作者、小型团队原型开发者。
- 自己决定是否 clone、部署和改造项目，不是企业采购者。

### Secondary

- 教师、培训内容作者和技术博主：需要一个可演示的 AI 应用案例。
- Hackathon 和独立开发者：需要快速生成或验证浏览器小游戏原型。
- 非技术游戏创作者是潜在最终用户，但在安装、模型密钥和托管体验简化前，不应作为仓库的首要受众。

## Where They Hang Out

- 中文：CSDN、掘金、知乎、哔哩哔哩、微信公众号、V2EX、GitHub 中文社区。
- 国际：GitHub、Dev.to、Hashnode、Hacker News、Reddit 的 LocalLLaMA、webdev、gamedev 社区。
- 搜索主题：AI 项目实战、LangGraph 实战、自然语言生成游戏、FastAPI + Vue、DeepSeek 接入、生成代码预览。
- GitHub topics：`ai-game-generator`、`langgraph`、`fastapi`、`vue3`、`llm-app`、`code-generation`、`html5-game`、`self-hosted`。

## Problems & Pain Points

- 教程常停留在单轮聊天，缺少项目状态、多轮修改、生成文件、预览和错误收尾的完整案例。
- 通用 AI 编程工具可用但实现不可见，不适合学习生成流程如何落地。
- 从零组合 LLM、工作流、数据库、SSE 和前端预览成本高，容易在生命周期和安全细节上踩坑。
- 想做一个可展示、可试玩的 AI 项目，而不是又一个聊天机器人。
- 待验证的原话假设："有没有一个能跑起来的 LangGraph 完整项目？"、"我想用自然语言生成一个可以直接玩的网页小游戏。"

## Current Alternatives

- **通用生成工具**：Replit Agent、Bolt、Lovable、Cursor；体验成熟，但通常不是游戏专用的开源参考实现。
- **游戏生成/创作工具**：Rosebud AI、GDevelop 等；更偏最终创作者体验，学习底层 AI 应用架构的空间有限。
- **DIY**：把 LangChain/LangGraph 教程、FastAPI、Vue 和数据库自行拼接；自由但耗时。
- **传统模板**：直接下载 HTML5 游戏模板再手工修改；稳定但缺少自然语言迭代。

## Key Differentiators

- 可查看和修改的开源完整应用，而不是黑盒在线生成器。
- 以小游戏作为可视、可试玩的生成产物，比普通文本聊天更容易理解与演示。
- 覆盖“描述 → 生成 → 文件 → 预览 → 继续修改”的项目生命周期。
- 可自托管并可替换模型 provider。
- 差异化必须用可运行 demo、测试和限制说明证明；暂不把 MCP、成熟 RAG、自动代码审查或未经验证的性能数字作为卖点。

## Verbatim Developer Language

当前没有真实用户访谈或 Issue 数据，以下只是需要通过评论、Issue 和搜索数据验证的候选表达：

- "LangGraph 有没有不是玩具聊天机器人的项目？"
- "DeepSeek 怎么接到 FastAPI + Vue 项目里？"
- "AI 生成的 HTML/CSS/JS 怎么实时预览？"
- "为什么继续生成把原来的代码覆盖了？"
- "这个项目不装 Docker 能不能跑？"

## Technical Trust Signals

- 必需：可复制的 quickstart、演示 GIF/视频、CI、自动测试、明确支持的模型、MIT 许可证。
- 必需：公开限制、安全说明、架构图、变更日志和版本化 release。
- 当前基线（2026-07-23）：GitHub 1 star、0 fork、无 topics、无 homepage、无公开 Issue；不能用采用量作为主要信任信号。
- 近期最有价值的证明：10 分钟内首次生成成功、示例项目、测试通过、真实问题复盘。

## Conversion Actions

- **Awareness**: 阅读技术文章或观看 demo；访问 GitHub。
- **Consideration**: 看完 README 首屏、架构图与限制；star 或收藏。
- **Trial**: clone；仅配置一个 LLM key；在 10 分钟内生成第一个可玩的 Web 游戏。
- **Activation**: 对已有游戏提出一次修改，预览仍保留原功能并加入新功能。
- **Community**: 提交 Issue、Discussion、示例游戏或第一个 PR。

## Voice & Tone

- 中文优先、可逐步提供英文版本。
- 友好、直接、技术可信、builder-first。
- 先展示能运行的结果，再解释实现。
- 主动说明限制和权衡；避免“企业级”“革命性”“90% 成功率”等无证据宣传。
- 内容以实际代码、命令、输出、截图和失败复盘为核心。

## Validation Queue

- 采访或收集至少 10 位目标开发者的实际问题。
- 从 CSDN、GitHub Issues、搜索联想和视频评论中记录原话。
- 测量从 README 到 clone、从 clone 到首次成功生成的漏斗。
- 根据反馈验证主要价值究竟是“学习完整 AI 应用”还是“快速制作小游戏”。
