# DreamCoder Domain Context

## Generation Run（生成运行）

一次用户请求驱动的完整游戏生成生命周期。它可以创建新项目，也可以在已完成项目的现有文件上继续生成；负责项目状态转换、工作流执行、生成步骤、聊天记录以及成功或失败收尾。

- **Generation Run module**：隐藏上述生命周期的 deep module。
- **Run ticket（运行票据）**：`begin` 成功后产生的不可变快照，包含项目、用户输入、现有文件、运行模式和工作流线程标识。
- **Route adapter**：把 HTTP 或 SSE 输入转换为 module interface 调用，不拥有生成事务或状态机。

## Generated Artifact（生成产物）

模型返回的一组文本文件。它在进入部署或浏览器预览前必须通过统一的路径、入口文件、数量和大小规则；生成内容始终被视为不可信输入。

- **Generated Artifact module**：集中验证可部署文件集合，并保证文件只能原子地写入指定部署目录。
- **Deployment adapter**：把已验证产物写入静态目录；不重新解释或放宽产物规则。
