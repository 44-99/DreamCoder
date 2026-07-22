"""
游戏生成工作流 - 基于LangGraph的AI游戏生成系统
使用状态图管理游戏生成流程，支持LangSmith追踪
"""


import os
import re
from functools import lru_cache
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from core.dependencies import logger
from modules.generated_artifact import ArtifactValidationError, GeneratedArtifact


# 定义游戏生成状态
class GameState(TypedDict):
    """游戏生成状态管理"""
    user_id: int
    user_input: str  # 用户自然语言输入
    existing_files: Optional[Dict[str, str]]  # 继续生成时的现有文件快照
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


# 初始化LLM - 支持多种模型提供商
@lru_cache(maxsize=1)
def get_llm():
    """根据环境变量选择LLM提供商"""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # 代码生成任务推荐使用较低的温度以保证稳定性和准确性
    code_gen_temp = float(os.getenv("CODE_GEN_TEMPERATURE", "0.2"))
    logger.info(
        "Using LLM provider: %s with temperature: %s",
        provider,
        code_gen_temp,
    )
    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_PROVIDER=deepseek requires DEEPSEEK_API_KEY")
        # DeepSeek 使用 OpenAI 兼容的 API
        # 官方推荐代码生成使用 temperature=0.0
        return ChatOpenAI(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            temperature=code_gen_temp,
            openai_api_key=api_key,
            openai_api_base=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
    elif provider == "qwen":
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_PROVIDER=qwen requires QWEN_API_KEY")
        # 通义千问 (阿里云)
        return ChatOpenAI(
            model=os.getenv("QWEN_MODEL", "qwen3.7-plus"),
            temperature=code_gen_temp,
            openai_api_key=api_key,
            openai_api_base=os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("LLM_PROVIDER=openai requires OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
        model_options = {
            "model": openai_model,
            "openai_api_key": api_key,
            "openai_api_base": os.getenv("OPENAI_BASE_URL"),
        }
        if openai_model.startswith("gpt-5.6"):
            # Structured output uses Chat Completions function tools.
            model_options["reasoning_effort"] = "none"
        else:
            model_options["temperature"] = code_gen_temp
        return ChatOpenAI(**model_options)


def get_provider():
    """获取当前LLM提供商"""
    return os.getenv("LLM_PROVIDER", "openai").lower()


def supports_structured_output():
    """检查当前提供商是否支持结构化输出"""
    provider = get_provider()
    # DeepSeek 等国内模型不支持 response_format
    unsupported_providers = ["deepseek", "qwen", "zhipu", "moonshot", "baichuan"]
    return provider not in unsupported_providers


def _response_text(response: Any) -> str:
    """Normalize text returned by OpenAI-compatible chat providers."""
    content = response.content
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        text = "\n".join(parts).strip()
    else:
        text = ""

    if not text:
        raise ValueError("模型返回了空文本响应")
    return text


def _parse_json_object(content: str, required_keys: set[str]) -> Dict[str, Any]:
    """Extract a JSON object even when a provider adds reasoning or prose."""
    decoder = json.JSONDecoder()
    missing_keys: set[str] = set()

    for index, character in enumerate(content):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue

        missing_keys = required_keys.difference(value)
        if not missing_keys:
            return value

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"模型 JSON 缺少必需字段: {missing}")
    raise ValueError("模型响应中未找到有效 JSON 对象")


def _parse_generated_files(content: str) -> Dict[str, str]:
    """Accept the documented JSON contract or a self-contained HTML response."""
    json_error: Optional[ValueError] = None
    try:
        value = _parse_json_object(content, {"files"})
        files = value["files"]
        if not isinstance(files, dict) or not all(
            isinstance(path, str) and isinstance(file_content, str)
            for path, file_content in files.items()
        ):
            raise ValueError("模型 JSON 的 files 必须是文本文件映射")
        return files
    except ValueError as exc:
        json_error = exc

    fenced = re.search(r"```(?:html)?\s*(.*?)```", content, re.IGNORECASE | re.DOTALL)
    candidates = [fenced.group(1)] if fenced else []
    candidates.append(content)

    for candidate in candidates:
        lower = candidate.lower()
        starts = [position for position in (lower.find("<!doctype html"), lower.find("<html")) if position >= 0]
        if not starts:
            continue
        start = min(starts)
        closing = lower.rfind("</html>")
        end = closing + len("</html>") if closing >= start else len(candidate)
        html = candidate[start:end].strip()
        if html:
            return {"index.html": html}

    raise json_error


# 1. 需求分析节点
async def requirement_analyzer_node(state: GameState) -> GameState:
    """分析用户需求，提取游戏规格"""
    logger.info(f"需求分析节点开始执行，用户输入: {state['user_input']}")

    try:
        llm = get_llm()
        if supports_structured_output():
            # 支持结构化输出的提供商（如 OpenAI）
            system_prompt = """
            你是一个游戏需求分析专家。分析用户的自然语言描述，提取游戏的关键信息。

            支持的游戏类型例如: 贪吃蛇, 打砖块, 打地鼠, 躲避球, 猜数字, 俄罗斯方块, 跳一跳, 弹球游戏
            """

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state['user_input'])
            ]

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
        else:
            # 不支持结构化输出的提供商（如 DeepSeek），使用 JSON 提示
            system_prompt = """
            你是一个游戏需求分析专家。分析用户的自然语言描述，提取游戏的关键信息。

            请严格按照以下JSON格式返回，不要有任何其他文字：
            {
                "game_type": "游戏类型",
                "core_mechanics": ["核心玩法机制1", "核心玩法机制2"],
                "visual_style": "视觉风格",
                "difficulty": "难度级别",
                "controls": ["控制方式1", "控制方式2"],
                "features": ["额外功能1", "额外功能2"]
            }

            游戏类型例如: 贪吃蛇, 打砖块, 打地鼠, 躲避球, 猜数字, 俄罗斯方块, 跳一跳, 弹球游戏

            视觉风格例如: 极简, 复古, 卡通, 现代化

            难度级别例如: 简单, 中等, 困难

            控制方式例如: 键盘方向键, WASD, 鼠标点击, 触摸

            额外功能例如: 计分系统, 等级系统, 音效, 动画效果
            """

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"""
                只分析下面的用户需求，不要生成 HTML、CSS 或 JavaScript。
                必须只返回 system message 指定字段组成的 JSON 对象。

                用户需求：
                {state['user_input']}
                """)
            ]

            response = await llm.ainvoke(messages)
            content = _response_text(response)
            try:
                requirements = _parse_json_object(
                    content,
                    {
                        "game_type",
                        "core_mechanics",
                        "visual_style",
                        "difficulty",
                        "controls",
                        "features",
                    },
                )
            except ValueError as parse_error:
                try:
                    generated_files = _parse_generated_files(content)
                except ValueError:
                    raise parse_error

                requirements = {
                    "game_type": "HTML5 游戏",
                    "core_mechanics": [state['user_input']],
                    "visual_style": "按用户描述",
                    "difficulty": "中等",
                    "controls": [],
                    "features": [],
                }
                state['requirements'] = requirements
                state['game_type'] = requirements['game_type']
                state['generated_files'] = generated_files
                state['logs'].append({
                    "step": "requirement_analyzer",
                    "status": "completed",
                    "message": "模型提前返回完整 HTML，已直接进入产物验证",
                    "timestamp": datetime.now().isoformat(),
                })
                state['current_step'] = "testing"
                return state

        state['requirements'] = requirements
        state['game_type'] = requirements.get('game_type', '未知')
        state['logs'].append({
            "step": "requirement_analyzer",
            "status": "completed",
            "message": f"需求分析完成: {state['game_type']}",
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
        llm = get_llm()
        if supports_structured_output():
            # 支持结构化输出的提供商
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
        else:
            # 不支持结构化输出的提供商，使用 JSON 提示
            prompt = f"""{system_prompt}

请严格按照以下JSON格式返回，不要有任何其他文字：
{{
    "tech_stack": "技术栈",
    "file_structure": {{
        "root": ["index.html", "styles.css"],
        "js": ["game.js"],
        "assets": []
    }},
    "main_components": ["组件1", "组件2"],
    "key_functions": ["函数1", "函数2"]
}}

游戏信息：
- 游戏类型: {requirements.get('game_type', '未知')}
- 核心机制: {', '.join(requirements.get('core_mechanics', []))}
- 视觉风格: {requirements.get('visual_style', '极简')}
- 难度: {requirements.get('difficulty', '中等')}
- 控制方式: {', '.join(requirements.get('controls', []))}
- 额外功能: {', '.join(requirements.get('features', []))}"""

            response = await llm.ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content="请生成架构设计")
            ])
            architecture = _parse_json_object(
                _response_text(response),
                {
                    "tech_stack",
                    "file_structure",
                    "main_components",
                    "key_functions",
                },
            )

        state['architecture'] = architecture
        state['logs'].append({
            "step": "architect_designer",
            "status": "completed",
            "message": f"架构设计完成，技术栈: {architecture.get('tech_stack', '未知')}",
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
    logger.info("代码生成节点开始执行")

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
    existing_files = state.get('existing_files') or {}

    continuation_context = ""
    if existing_files:
        continuation_context = f"""

            这是一次现有项目改进。请基于下面的完整文件集合实现用户的新需求，
            保留未要求删除的功能，并在 files 中返回改进后的完整文件集合：
            {json.dumps(existing_files, ensure_ascii=False)}
            """

    try:
        llm = get_llm()
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
            {continuation_context}
             """)
        ]

        response = await llm.ainvoke(messages)
        content = _response_text(response)

        # 解析生成的文件
        # 简单处理：期望返回JSON格式的files字段
        try:
            generated_files = _parse_generated_files(content)

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

        except ValueError as e:
            # 如果JSON解析失败，尝试生成基础代码
            logger.warning(f"JSON解析失败，使用基础代码生成: {e}")

            # 生成一个简单的贪吃蛇游戏作为后备
            fallback_files = existing_files or generate_simple_snake_game()
            state['generated_files'] = fallback_files
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
        state['generated_files'] = existing_files or generate_simple_snake_game()
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
    logger.info("测试验证节点开始执行")

    try:
        files = state.get('generated_files', {})

        artifact_error = None
        try:
            artifact = GeneratedArtifact.from_mapping(files)
            artifact_result = {
                "test": "生成产物安全",
                "passed": True,
                "message": f"✓ {len(artifact.files)} 个文件通过路径和大小校验",
            }
        except ArtifactValidationError as exc:
            artifact_error = str(exc)
            artifact_result = {
                "test": "生成产物安全",
                "passed": False,
                "message": f"✗ {artifact_error}",
            }

        # 基本验证
        validation_results = [
            artifact_result,
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
        if artifact_error:
            state['error'] = f"生成产物校验失败: {artifact_error}"
        state['logs'].append({
            "step": "test_validator",
            "status": "failed" if artifact_error else "completed",
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
    logger.info("部署节点开始执行")

    try:
        if state.get('error'):
            state['logs'].append({
                "step": "deployment",
                "status": "skipped",
                "message": "生成产物存在错误，已跳过部署",
                "timestamp": datetime.now().isoformat(),
            })
            return state

        user_id = state['user_id']
        files = state.get('generated_files', {})
        artifact = GeneratedArtifact.from_mapping(files)

        # Deploy a validated artifact into a unique directory.
        projects_dir = Path(os.getenv('PROJECTS_DIR', './generated_projects'))
        deployment_name = (
            f"project_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
            f"{uuid4().hex[:8]}"
        )
        project_dir = artifact.deploy(projects_dir, deployment_name)

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


def _route_after_step(state: GameState) -> str:
    return "stop" if state.get("error") else "continue"


def _route_after_requirement(state: GameState) -> str:
    if state.get("error"):
        return "stop"
    if state.get("generated_files"):
        return "test"
    return "continue"


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

    # Stop immediately after a failed node instead of cascading secondary errors.
    workflow.add_conditional_edges(
        "requirement_analyzer",
        _route_after_requirement,
        {"continue": "architect_designer", "test": "test_validator", "stop": END},
    )
    workflow.add_conditional_edges(
        "architect_designer",
        _route_after_step,
        {"continue": "code_generator", "stop": END},
    )
    workflow.add_conditional_edges(
        "code_generator",
        _route_after_step,
        {"continue": "test_validator", "stop": END},
    )
    workflow.add_conditional_edges(
        "test_validator",
        _route_after_step,
        {"continue": "deployment", "stop": END},
    )
    workflow.add_edge("deployment", END)

    # 添加检查点（用于恢复和追踪）
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app


# 初始化工作流
game_generation_app = create_game_generation_workflow()


async def run_game_generation(
    user_id: int,
    user_input: str,
    existing_files: Optional[Dict[str, str]] = None,
    thread_id: str = None,
):
    """运行游戏生成流程"""
    initial_state = {
        "user_id": user_id,
        "user_input": user_input,
        "existing_files": existing_files,
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
