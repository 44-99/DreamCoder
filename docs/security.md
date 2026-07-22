# DreamCoder 安全边界

DreamCoder 会执行和展示模型生成的 HTML/CSS/JavaScript。生成内容必须被当作不可信输入，而不是普通模板文件。

## 当前已有的保护

- Generated Artifact module 拒绝绝对路径、`..` 路径穿越、过多文件和过大内容。
- 只有通过统一校验的文件集合才会写入静态项目目录。
- 写入先发生在临时目录，再原子替换目标目录，避免留下部分产物。
- 前端为预览文档注入 CSP，并使用最小 `iframe sandbox="allow-scripts"`。
- 默认 CSP 禁止网络连接、表单提交、顶层导航、插件对象和远程资源。
- API Key 只从后端环境变量读取，不应进入前端 bundle、Issue、日志或截图。

对应实现：

- `backend/modules/generated_artifact.py`
- `frontend/src/utils/htmlGenerator.js`
- `frontend/src/views/GameChatView.vue`

## 这不代表什么

当前保护不等于完整沙箱或安全审计。特别是：

- 预览与主应用仍由同一站点提供；
- 浏览器和 CSP 实现可能存在未知绕过；
- 生成代码校验主要是路径和启发式规则，不证明业务逻辑安全；
- 多租户对抗性场景尚未经过独立渗透测试。

不要把当前版本直接用于运行匿名互联网用户提交的任意代码。

## 本地开发与公开部署

| 项目 | 本地默认 | 公开部署要求 |
|---|---|---|
| 验证码渠道 | 控制台开发码 | `AUTH_DELIVERY_MODE=external` + SMTP/短信 |
| JWT 密钥 | 示例值 | 高熵、独立、受密钥管理保护的 `SECRET_KEY` |
| 数据库 | SQLite | 根据并发与备份要求选择 PostgreSQL |
| 验证码状态 | 进程内 | 多实例时启用 Redis |
| CORS | 仅本机前端 origin | 用 `CORS_ALLOWED_ORIGINS` 设置实际前端 origin |
| 预览 | 同源静态路径 | 独立 origin 或一次性隔离容器 |
| TLS | 无 | HTTPS 与安全响应头 |

## 密钥处理

- 只把真实 Key 写入未跟踪的 `backend/.env` 或部署平台的 secret store。
- 提交前运行 `git diff --cached`，确认没有凭据、数据库或个人信息。
- 如果 Key 曾进入 Git 历史，立即在 provider 控制台撤销；仅从最新文件删除并不够。
- 日志和 bug 报告应移除请求头、token、手机号、邮箱与完整模型响应中的敏感内容。

## 漏洞报告

请优先使用 GitHub Private Vulnerability Reporting。公开 Issue 不应包含可直接利用的细节或真实凭据。

## 安全 Roadmap

1. 将预览迁移到独立 origin 或隔离容器；
2. 为生产模式加入严格的配置启动检查；
3. 增加浏览器级恶意样例回归测试；
4. 在支持公共多租户之前安排独立安全评审。
