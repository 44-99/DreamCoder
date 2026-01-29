# DreamCoder - AI游戏生成系统

基于 LangChain/LangGraph 的智能游戏生成平台，通过自然语言描述自动生成可运行的Web游戏项目。

## 🚀 核心特性

- **AI驱动**: 使用 GPT-4o-mini 进行智能需求分析、架构设计和代码生成
- **LangGraph工作流**: 状态图管理游戏生成全流程，支持追踪和恢复
- **RAG知识库**: ChromaDB向量检索相似游戏模板
- **MCP工具**: 文件系统、终端等工具调用支持
- **实时预览**: 生成的游戏支持即时预览
- **代码审查**: 自动生成质量评分和测试报告

## 🛠️ 技术栈

### 后端
- **FastAPI**: 高性能Web框架
- **LangChain**: LLM应用开发框架
- **LangGraph**: 状态图工作流编排
- **LangSmith**: 应用追踪和调试
- **PostgreSQL**: 关系型数据库
- **Redis**: 缓存和消息队列
- **ChromaDB**: 向量数据库

### 前端
- **Vue 3**: 渐进式前端框架
- **Vite**: 快速构建工具
- **Pinia**: 状态管理
- **Vue Router**: 路由管理

## 📦 快速开始

### 环境要求
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### 本地开发

1. **克隆项目**
```bash
git clone https://github.com/44-99/DreamCoder.git
cd DreamCoder
```

2. **配置环境变量**
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入必要的配置
```

3. **启动数据库服务**
```bash
docker-compose up postgres redis -d
```

4. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

5. **启动后端服务**
```bash
uvicorn main:app --reload
```

6. **安装前端依赖**
```bash
cd ../frontend
npm install
```

7. **启动前端服务**
```bash
npm run dev
```

### Docker 部署

开发模式（包含前后端）:
```bash
docker-compose --profile dev up -d
```

生产模式:
```bash
# 先构建前端
cd frontend
npm run build

# 启动服务
cd ..
docker-compose --profile production up -d
```

访问:
- 前端: http://localhost:5173 (开发) 或 http://localhost (生产)
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🎮 使用示例

1. **注册/登录**
   - 访问登录页面
   - 输入用户名、密码和验证码完成注册

2. **生成游戏**
   - 在游戏生成器页面描述你想要的游戏
   - 例如: "我想要一个贪吃蛇游戏，可以用方向键控制蛇吃食物"
   - 点击"开始生成"

3. **预览和编辑**
   - 实时查看生成进度日志
   - 在预览区域试玩游戏
   - 查看和编辑生成的源代码
   - 查看项目信息和质量评分

4. **历史管理**
   - 在历史项目页面查看所有生成的游戏
   - 重新加载和预览历史项目

## 📁 项目结构

```
DreamCoder/
├── backend/
│   ├── core/              # 核心模块
│   │   ├── models.py      # 数据库模型
│   │   ├── dependencies.py # 依赖配置
│   │   ├── knowledge_base.py # RAG知识库
│   │   └── mcp_tool_manager.py # MCP工具管理
│   ├── workflows/         # LangGraph工作流
│   │   └── game_gen_workflow.py
│   ├── routers/          # API路由
│   │   ├── auth.py       # 认证
│   │   ├── user.py       # 用户管理
│   │   └── game_generation.py # 游戏生成
│   ├── static/           # 静态资源
│   └── main.py           # FastAPI入口
├── frontend/
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   │   ├── LoginView.vue
│   │   │   ├── ProfileView.vue
│   │   │   └── GameGeneratorView.vue
│   │   ├── stores/       # 状态管理
│   │   └── router/       # 路由配置
│   └── package.json
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker镜像
└── nginx.conf           # Nginx配置
```

## 🔧 API接口

### 认证
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/verification` - 发送验证码

### 游戏生成
- `POST /game/generate` - 生成游戏
- `GET /game/generate/stream` - 流式生成（SSE）
- `GET /game/projects` - 获取项目列表
- `GET /game/projects/{id}` - 获取项目详情
- `GET /game/projects/{id}/files` - 获取项目文件
- `GET /game/projects/{id}/logs` - 获取生成日志
- `GET /game/templates` - 获取游戏模板
- `GET /game/templates/search` - 搜索模板

## 📊 性能指标

- **生成速度**: ~45秒/项目
- **成功率**: >90%
- **代码质量评分**: 平均85/100

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

Apache License 2.0
