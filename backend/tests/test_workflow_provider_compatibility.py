import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from workflows import game_gen_workflow  # noqa: E402


class _FakeResponse:
    def __init__(self, content: str):
        self.content = content


class _FakeLlm:
    def __init__(self, content: str):
        self._content = content

    async def ainvoke(self, _messages):
        return _FakeResponse(self._content)


class WorkflowProviderCompatibilityTests(unittest.TestCase):
    def test_reasoning_wrapped_json_is_parsed(self):
        state = {
            "user_id": 1,
            "user_input": "生成一个贪吃蛇游戏",
            "logs": [],
            "current_step": "started",
            "error": None,
        }
        response = """<think>先提取用户要求。</think>
        {
          "game_type": "贪吃蛇",
          "core_mechanics": ["移动", "吃食物"],
          "visual_style": "复古",
          "difficulty": "中等",
          "controls": ["键盘方向键"],
          "features": ["计分系统", "暂停"]
        }"""

        with (
            patch.object(game_gen_workflow, "get_llm", return_value=_FakeLlm(response)),
            patch.object(
                game_gen_workflow,
                "supports_structured_output",
                return_value=False,
            ),
        ):
            result = asyncio.run(game_gen_workflow.requirement_analyzer_node(state))

        self.assertIsNone(result["error"])
        self.assertEqual("贪吃蛇", result["requirements"]["game_type"])

    def test_fenced_html_is_used_as_single_file_model_output(self):
        state = {
            "user_id": 1,
            "user_input": "生成一个单文件贪吃蛇游戏",
            "requirements": {
                "game_type": "贪吃蛇",
                "core_mechanics": ["移动"],
                "visual_style": "复古",
                "difficulty": "中等",
                "controls": ["键盘方向键"],
                "features": ["计分系统"],
            },
            "architecture": {
                "tech_stack": "Vanilla JS",
                "main_components": ["Game"],
            },
            "existing_files": None,
            "logs": [],
            "current_step": "code_generation",
            "error": None,
        }
        response = """<think>生成一个自包含页面。</think>
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>MODEL_OUTPUT_MARKER</title></head>
<body><canvas id="game"></canvas><script>document.addEventListener('keydown', () => {});</script></body>
</html>
```"""

        with patch.object(
            game_gen_workflow,
            "get_llm",
            return_value=_FakeLlm(response),
        ):
            result = asyncio.run(game_gen_workflow.code_generator_node(state))

        self.assertIsNone(result["error"])
        self.assertIn("MODEL_OUTPUT_MARKER", result["generated_files"]["index.html"])
        self.assertNotEqual("使用基础模板生成代码", result["logs"][-1]["message"])

    def test_requirement_step_accepts_complete_html_returned_early(self):
        state = {
            "user_id": 1,
            "user_input": "生成一个单文件贪吃蛇游戏",
            "requirements": None,
            "generated_files": None,
            "logs": [],
            "current_step": "started",
            "error": None,
        }
        response = """我直接提供完整游戏：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>EARLY_MODEL_OUTPUT</title></head>
<body><canvas></canvas><script>document.addEventListener('keydown', () => {});</script></body>
</html>
```"""

        with (
            patch.object(game_gen_workflow, "get_llm", return_value=_FakeLlm(response)),
            patch.object(
                game_gen_workflow,
                "supports_structured_output",
                return_value=False,
            ),
        ):
            result = asyncio.run(game_gen_workflow.requirement_analyzer_node(state))

        self.assertIsNone(result["error"])
        self.assertIn("EARLY_MODEL_OUTPUT", result["generated_files"]["index.html"])
        self.assertEqual("testing", result["current_step"])

    def test_error_short_circuits_remaining_nodes(self):
        calls = []

        async def failing_requirement(state):
            calls.append("requirement_analyzer")
            state["error"] = "需求分析失败"
            return state

        def tracked_node(name):
            async def node(state):
                calls.append(name)
                return state

            return node

        with (
            patch.object(
                game_gen_workflow,
                "requirement_analyzer_node",
                new=failing_requirement,
            ),
            patch.object(
                game_gen_workflow,
                "architect_designer_node",
                new=tracked_node("architect_designer"),
            ),
            patch.object(
                game_gen_workflow,
                "code_generator_node",
                new=tracked_node("code_generator"),
            ),
            patch.object(
                game_gen_workflow,
                "test_validator_node",
                new=tracked_node("test_validator"),
            ),
            patch.object(
                game_gen_workflow,
                "deployment_node",
                new=tracked_node("deployment"),
            ),
        ):
            app = game_gen_workflow.create_game_generation_workflow()
            result = asyncio.run(
                app.ainvoke(
                    {
                        "user_id": 1,
                        "user_input": "生成一个贪吃蛇游戏",
                        "existing_files": None,
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
                        "error": None,
                    },
                    {"configurable": {"thread_id": "short-circuit-test"}},
                )
            )

        self.assertEqual("需求分析失败", result["error"])
        self.assertEqual(["requirement_analyzer"], calls)


if __name__ == "__main__":
    unittest.main()
