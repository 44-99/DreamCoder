"""
游戏生成工作流 - 基于LangGraph的AI游戏生成系统
使用状态图管理游戏生成流程，支持LangSmith追踪
"""
import os
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from core.dependencies import logger


# 定义游戏生成状态
class GameState(TypedDict):
    """游戏生成状态管理"""
    user_id: int
    user_input: str  # 用户自然语言输入
    game_type: Optional[str]  # 游戏类型
    requirements: Optional[Dict[str, Any]]  # 需求分析结果
    selected_template: Optional[Dict[str, Any]]  # 选中的模板
    architecture: Optional[Dict[str, Any]]  # 架构设计
    generated_files: Optional[Dict[str, str]]  # 生成的文件 {path: content}
    test_results: Optional[List[Dict[str, Any]]]  # 测试结果
    deployment_url: Optional[str]  # 部署URL
    quality_score: Optional[float]  # 质量评分
    logs: List[Dict[str, Any]]  # 执行日志
    current_step: str  # 当前步骤
    error: Optional[str]  # 错误信息


# Pydantic模型用于结构化输出
class GameRequirements(BaseModel):
    """游戏需求分析结果"""
    game_type: str = Field(description="游戏类型: 贪吃蛇, 打砖块, 打地鼠, 躲避球, 猜数字, 俄罗斯方块")
    core_mechanics: List[str] = Field(description="核心玩法机制列表")
    visual_style: str = Field(description="视觉风格: 极简, 复古, 卡通, 现代化")
    difficulty: str = Field(description="难度级别: 简单, 中等, 困难")
    controls: List[str] = Field(description="控制方式: 键盘方向键, WASD, 鼠标点击, 触摸")
    features: List[str] = Field(description="额外功能: 计分系统, 等级系统, 音效, 动画效果")


class GameArchitecture(BaseModel):
    """游戏架构设计"""
    tech_stack: str = Field(description="技术栈: Vanilla JS, Canvas API, Phaser 3, Pygame")
    file_structure: Dict[str, List[str]] = Field(description="文件结构")
    main_components: List[str] = Field(description="主要组件列表")
    key_functions: List[str] = Field(description="关键函数列表")


class FileGenerationResult(BaseModel):
    """文件生成结果"""
    file_path: str = Field(description="文件路径")
    content: str = Field(description="文件内容")
    language: str = Field(description="编程语言")


# 初始化LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL")
)


# 1. 需求分析节点
async def requirement_analyzer_node(state: GameState) -> GameState:
    """分析用户需求，提取游戏规格"""
    logger.info(f"需求分析节点开始执行，用户输入: {state['user_input']}")

    system_prompt = """
    你是一个游戏需求分析专家。分析用户的自然语言描述，提取游戏的关键信息。

    请按照以下格式返回JSON：
    - game_type: 游戏类型
    - core_mechanics: 核心玩法机制
    - visual_style: 视觉风格
    - difficulty: 难度级别
    - controls: 控制方式
    - features: 额外功能

    支持的游戏类型包括: 贪吃蛇, 打砖块, 打地鼠, 躲避球, 猜数字, 俄罗斯方块, 跳一跳, 弹球游戏
    """

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state['user_input'])
        ]

        # 使用结构化输出
        structured_llm = llm.with_structured_output(GameRequirements)
        result = await structured_llm.ainvoke(messages)

        requirements = {
            "game_type": result.game_type,
            "core_mechanics": result.core_mechanics,
            "visual_style": result.visual_style,
            "difficulty": result.difficulty,
            "controls": result.controls,
            "features": result.features
        }

        state['requirements'] = requirements
        state['game_type'] = result.game_type
        state['logs'].append({
            "step": "requirement_analyzer",
            "status": "completed",
            "message": f"需求分析完成: {result.game_type}",
            "timestamp": datetime.now().isoformat()
        })
        state['current_step'] = "architecture_design"

        logger.info(f"需求分析完成: {requirements}")
        return state

    except Exception as e:
        logger.error(f"需求分析失败: {e}")
        state['error'] = f"需求分析失败: {str(e)}"
        return state


# 2. 架构设计节点
async def architect_designer_node(state: GameState) -> GameState:
    """设计游戏架构"""
    logger.info(f"架构设计节点开始执行，游戏类型: {state['game_type']}")

    system_prompt = """
    你是一个游戏架构设计师。根据需求设计游戏的技术架构。

    技术栈选择原则:
    - 贪吃蛇, 打地鼠, 躲避球, 猜数字 -> Vanilla JS + Canvas API
    - 打砖块, 俄罗斯方块 -> Vanilla JS + Canvas API
    - 复杂游戏 -> Phaser 3

    请设计清晰的文件结构，包括:
    - index.html: 主页面
    - styles.css: 样式文件
    - game.js: 游戏主逻辑
    - assets/: 图片资源
    """

    requirements = state.get('requirements', {})

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            游戏类型: {requirements.get('game_type', '未知')}
            核心机制: {', '.join(requirements.get('core_mechanics', []))}
            视觉风格: {requirements.get('visual_style', '极简')}
            难度: {requirements.get('difficulty', '中等')}
            控制方式: {', '.join(requirements.get('controls', []))}
            额外功能: {', '.join(requirements.get('features', []))}
            """)
        ]

        structured_llm = llm.with_structured_output(GameArchitecture)
        result = await structured_llm.ainvoke(messages)

        architecture = {
            "tech_stack": result.tech_stack,
            "file_structure": result.file_structure,
            "main_components": result.main_components,
            "key_functions": result.key_functions
        }

        state['architecture'] = architecture
        state['logs'].append({
            "step": "architect_designer",
            "status": "completed",
            "message": f"架构设计完成，技术栈: {result.tech_stack}",
            "timestamp": datetime.now().isoformat()
        })
        state['current_step'] = "code_generation"

        logger.info(f"架构设计完成: {architecture}")
        return state

    except Exception as e:
        logger.error(f"架构设计失败: {e}")
        state['error'] = f"架构设计失败: {str(e)}"
        return state


# 3. 代码生成节点
async def code_generator_node(state: GameState) -> GameState:
    """生成游戏代码"""
    logger.info(f"代码生成节点开始执行")

    system_prompt = """
    你是一个游戏代码生成专家。生成完整、可运行的游戏代码。

    代码要求:
    1. HTML文件需要包含完整的DOCTYPE和head
    2. JavaScript代码要完整，包含所有游戏逻辑
    3. CSS样式要美观，支持响应式
    4. 代码要有良好的注释
    5. 游戏需要包含开始、暂停、重新开始功能
    6. 需要计分系统
    7. 需要游戏结束提示

    请按照以下格式返回JSON:
    - files: 文件列表 {文件路径: 文件内容}
    """

    requirements = state.get('requirements', {})
    architecture = state.get('architecture', {})

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
            生成一个{requirements.get('game_type', '游戏')}的完整代码。

            需求:
            - 游戏类型: {requirements.get('game_type', '未知')}
            - 核心机制: {', '.join(requirements.get('core_mechanics', []))}
            - 视觉风格: {requirements.get('visual_style', '极简')}
            - 难度: {requirements.get('difficulty', '中等')}
            - 控制方式: {', '.join(requirements.get('controls', []))}
            - 额外功能: {', '.join(requirements.get('features', []))}

            架构:
            - 技术栈: {architecture.get('tech_stack', 'Vanilla JS')}
            - 主要组件: {', '.join(architecture.get('main_components', []))}
            """)
        ]

        response = await llm.ainvoke(messages)
        content = response.content

        # 解析生成的文件
        # 简单处理：期望返回JSON格式的files字段
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            files_data = json.loads(content.strip())
            generated_files = files_data.get('files', {})

            # 确保至少有index.html
            if 'index.html' not in generated_files:
                raise ValueError("未生成index.html文件")

            state['generated_files'] = generated_files
            state['logs'].append({
                "step": "code_generator",
                "status": "completed",
                "message": f"代码生成完成，共{len(generated_files)}个文件",
                "timestamp": datetime.now().isoformat()
            })
            state['current_step'] = "testing"

            logger.info(f"代码生成完成，文件数: {len(generated_files)}")
            return state

        except json.JSONDecodeError as e:
            # 如果JSON解析失败，尝试生成基础代码
            logger.warning(f"JSON解析失败，使用基础代码生成: {e}")

            # 生成一个简单的贪吃蛇游戏作为后备
            simple_game = generate_simple_snake_game()
            state['generated_files'] = simple_game
            state['logs'].append({
                "step": "code_generator",
                "status": "completed",
                "message": "使用基础模板生成代码",
                "timestamp": datetime.now().isoformat()
            })
            state['current_step'] = "testing"
            return state

    except Exception as e:
        logger.error(f"代码生成失败: {e}")
        state['error'] = f"代码生成失败: {str(e)}"
        # 返回基础游戏
        state['generated_files'] = generate_simple_snake_game()
        state['logs'].append({
            "step": "code_generator",
            "status": "fallback",
            "message": "使用后备模板",
            "timestamp": datetime.now().isoformat()
        })
        state['current_step'] = "testing"
        return state


def generate_simple_snake_game() -> Dict[str, str]:
    """生成简单的贪吃蛇游戏代码"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贪吃蛇游戏</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: Arial, sans-serif;
        }
        .game-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }
        .score {
            text-align: center;
            font-size: 24px;
            margin-bottom: 10px;
            color: #667eea;
        }
        canvas {
            border: 3px solid #333;
            border-radius: 5px;
            display: block;
            margin: 0 auto;
        }
        .controls {
            text-align: center;
            margin-top: 15px;
            color: #666;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background: #764ba2;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>🐍 贪吃蛇</h1>
        <div class="score">得分: <span id="score">0</span></div>
        <canvas id="gameCanvas" width="400" height="400"></canvas>
        <div class="controls">
            <button onclick="startGame()">开始游戏</button>
            <button onclick="resetGame()">重新开始</button>
            <p>使用方向键或WASD控制蛇的移动</p>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const gridSize = 20;
        const tileCount = canvas.width / gridSize;

        let snake = [{x: 10, y: 10}];
        let food = {x: 15, y: 15};
        let dx = 0;
        let dy = 0;
        let score = 0;
        let gameLoop;
        let isGameRunning = false;

        function drawGame() {
            // 清空画布
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制食物
            ctx.fillStyle = '#ff6b6b';
            ctx.beginPath();
            ctx.arc(
                food.x * gridSize + gridSize/2,
                food.y * gridSize + gridSize/2,
                gridSize/2 - 2,
                0,
                Math.PI * 2
            );
            ctx.fill();

            // 绘制蛇
            snake.forEach((segment, index) => {
                ctx.fillStyle = index === 0 ? '#51cf66' : '#8ce99a';
                ctx.fillRect(
                    segment.x * gridSize + 1,
                    segment.y * gridSize + 1,
                    gridSize - 2,
                    gridSize - 2
                );
            });
        }

        function moveSnake() {
            const head = {
                x: snake[0].x + dx,
                y: snake[0].y + dy
            };

            // 检查是否撞墙
            if (head.x < 0 || head.x >= tileCount ||
                head.y < 0 || head.y >= tileCount) {
                gameOver();
                return;
            }

            // 检查是否撞到自己
            if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
                gameOver();
                return;
            }

            snake.unshift(head);

            // 检查是否吃到食物
            if (head.x === food.x && head.y === food.y) {
                score += 10;
                document.getElementById('score').textContent = score;
                generateFood();
            } else {
                snake.pop();
            }

            drawGame();
        }

        function generateFood() {
            food = {
                x: Math.floor(Math.random() * tileCount),
                y: Math.floor(Math.random() * tileCount)
            };
            // 确保食物不在蛇身上
            while (snake.some(segment => segment.x === food.x && segment.y === food.y)) {
                food = {
                    x: Math.floor(Math.random() * tileCount),
                    y: Math.floor(Math.random() * tileCount)
                };
            }
        }

        function gameOver() {
            clearInterval(gameLoop);
            isGameRunning = false;
            alert(`游戏结束！得分: ${score}`);
        }

        function startGame() {
            if (isGameRunning) return;
            isGameRunning = true;
            gameLoop = setInterval(moveSnake, 100);
        }

        function resetGame() {
            clearInterval(gameLoop);
            isGameRunning = false;
            snake = [{x: 10, y: 10}];
            dx = 0;
            dy = 0;
            score = 0;
            document.getElementById('score').textContent = score;
            generateFood();
            drawGame();
        }

        // 键盘控制
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    if (dy !== 1) { dx = 0; dy = -1; }
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    if (dy !== -1) { dx = 0; dy = 1; }
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    if (dx !== 1) { dx = -1; dy = 0; }
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    if (dx !== -1) { dx = 1; dy = 0; }
                    break;
            }
        });

        // 初始化
        generateFood();
        drawGame();
    </script>
</body>
</html>"""

    return {
        'index.html': html_content,
        'README.md': '# 贪吃蛇游戏\n\n使用方向键或WASD控制蛇的移动。'
    }


# 4. 测试验证节点
async def test_validator_node(state: GameState) -> GameState:
    """验证生成的代码"""
    logger.info(f"测试验证节点开始执行")

    try:
        files = state.get('generated_files', {})

        # 基本验证
        validation_results = [
            {
                "test": "HTML文件存在",
                "passed": 'index.html' in files,
                "message": "✓ 存在index.html" if 'index.html' in files else "✗ 缺少index.html"
            },
            {
                "test": "代码完整性",
                "passed": len(files.get('index.html', '')) > 1000,
                "message": "✓ 代码长度足够" if len(files.get('index.html', '')) > 1000 else "✗ 代码太短"
            },
            {
                "test": "游戏逻辑",
                "passed": 'canvas' in files.get('index.html', '').lower(),
                "message": "✓ 包含canvas游戏元素" if 'canvas' in files.get('index.html', '').lower() else "✗ 缺少游戏元素"
            },
            {
                "test": "交互功能",
                "passed": 'addEventListener' in files.get('index.html', ''),
                "message": "✓ 包含事件监听" if 'addEventListener' in files.get('index.html', '') else "✗ 缺少交互功能"
            }
        ]

        all_passed = all(result['passed'] for result in validation_results)
        quality_score = sum(1 for r in validation_results if r['passed']) / len(validation_results) * 100

        state['test_results'] = validation_results
        state['quality_score'] = quality_score
        state['logs'].append({
            "step": "test_validator",
            "status": "completed",
            "message": f"测试完成，质量评分: {quality_score}",
            "timestamp": datetime.now().isoformat()
        })

        if all_passed:
            state['current_step'] = "deployment"
        else:
            state['current_step'] = "deployment"  # 即使测试失败也部署，让用户预览

        logger.info(f"测试验证完成，质量评分: {quality_score}")
        return state

    except Exception as e:
        logger.error(f"测试验证失败: {e}")
        state['error'] = f"测试验证失败: {str(e)}"
        return state


# 5. 部署节点
async def deployment_node(state: GameState) -> GameState:
    """部署游戏项目"""
    logger.info(f"部署节点开始执行")

    try:
        user_id = state['user_id']
        files = state.get('generated_files', {})

        # 创建项目目录
        projects_dir = Path(os.getenv('PROJECTS_DIR', './generated_projects'))
        project_dir = projects_dir / f"project_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        project_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        for file_path, content in files.items():
            file_full_path = project_dir / file_path
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            file_full_path.write_text(content, encoding='utf-8')

        # 计算相对URL
        deployment_url = f"/static/projects/{project_dir.name}/index.html"

        state['deployment_url'] = deployment_url
        state['logs'].append({
            "step": "deployment",
            "status": "completed",
            "message": f"部署完成: {deployment_url}",
            "timestamp": datetime.now().isoformat()
        })
        state['current_step'] = "completed"

        logger.info(f"部署完成: {deployment_url}")
        return state

    except Exception as e:
        logger.error(f"部署失败: {e}")
        state['error'] = f"部署失败: {str(e)}"
        return state


# 创建工作流图
def create_game_generation_workflow():
    """创建游戏生成工作流"""
    workflow = StateGraph(GameState)

    # 添加节点
    workflow.add_node("requirement_analyzer", requirement_analyzer_node)
    workflow.add_node("architect_designer", architect_designer_node)
    workflow.add_node("code_generator", code_generator_node)
    workflow.add_node("test_validator", test_validator_node)
    workflow.add_node("deployment", deployment_node)

    # 设置入口
    workflow.set_entry_point("requirement_analyzer")

    # 添加边（线性流程）
    workflow.add_edge("requirement_analyzer", "architect_designer")
    workflow.add_edge("architect_designer", "code_generator")
    workflow.add_edge("code_generator", "test_validator")
    workflow.add_edge("test_validator", "deployment")
    workflow.add_edge("deployment", END)

    # 添加检查点（用于恢复和追踪）
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# 初始化工作流
game_generation_app = create_game_generation_workflow()


async def run_game_generation(user_id: int, user_input: str, thread_id: str = None):
    """运行游戏生成流程"""
    initial_state = {
        "user_id": user_id,
        "user_input": user_input,
        "game_type": None,
        "requirements": None,
        "selected_template": None,
        "architecture": None,
        "generated_files": None,
        "test_results": None,
        "deployment_url": None,
        "quality_score": None,
        "logs": [],
        "current_step": "started",
        "error": None
    }

    config = {
        "configurable": {
            "thread_id": thread_id or f"gen_{user_id}_{int(datetime.now().timestamp())}"
        }
    }

    try:
        result_state = await game_generation_app.ainvoke(initial_state, config)
        return result_state
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        initial_state['error'] = str(e)
        return initial_state
