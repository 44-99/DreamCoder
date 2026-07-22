import asyncio
import sys
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.dependencies import Base  # noqa: E402
from core.models import ChatMessage, GameProject, GenerationStep  # noqa: E402
from modules.generation_run import (  # noqa: E402
    GenerationRunModule,
    ProjectNotReadyError,
)


class GenerationRunModuleTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine)
        self.sessions = sessionmaker(bind=engine, expire_on_commit=False)

    def test_new_run_persists_complete_lifecycle(self):
        calls = []

        async def runner(user_id, user_input, existing_files, thread_id):
            calls.append((user_id, user_input, existing_files, thread_id))
            return {
                "generated_files": {"index.html": "<canvas></canvas>"},
                "deployment_url": "/preview/index.html",
                "quality_score": 75.0,
                "requirements": {"game_type": "贪吃蛇"},
                "architecture": {"tech_stack": "Vanilla JS"},
                "logs": [
                    {
                        "step": "code_generator",
                        "status": "completed",
                        "message": "生成完成",
                        "timestamp": "2026-07-22T12:00:00+00:00",
                    }
                ],
                "error": None,
            }

        module = GenerationRunModule(self.sessions, runner)
        ticket = module.begin(user_id=7, user_input="生成贪吃蛇", title="测试项目")
        outcome = asyncio.run(module.execute(ticket))

        self.assertTrue(ticket.is_creating_from_scratch)
        self.assertIsNone(calls[0][2])
        self.assertEqual("completed", outcome.status)
        with self.sessions() as db:
            project = db.query(GameProject).one()
            self.assertEqual("completed", project.status)
            self.assertEqual({"index.html": "<canvas></canvas>"}, project.files)
            self.assertEqual(1, db.query(GenerationStep).count())
            self.assertEqual(3, db.query(ChatMessage).count())

    def test_continuation_passes_existing_files_to_workflow(self):
        received = []

        async def runner(user_id, user_input, existing_files, thread_id):
            received.append(existing_files)
            return {
                "generated_files": {
                    **existing_files,
                    "feature.js": "console.log('new')",
                },
                "logs": [],
                "error": None,
            }

        with self.sessions() as db:
            project = GameProject(
                user_id=8,
                title="已有项目",
                description="初始需求",
                status="completed",
                files={"index.html": "old"},
            )
            db.add(project)
            db.commit()
            project_id = project.id

        module = GenerationRunModule(self.sessions, runner)
        ticket = module.begin(
            user_id=8,
            user_input="增加新功能",
            project_id=project_id,
        )
        outcome = asyncio.run(module.execute(ticket))

        self.assertFalse(ticket.is_creating_from_scratch)
        self.assertEqual({"index.html": "old"}, received[0])
        self.assertEqual("completed", outcome.status)
        with self.sessions() as db:
            project = db.query(GameProject).one()
            self.assertIn("feature.js", project.files)
            self.assertIn("用户补充需求: 增加新功能", project.description)

    def test_project_must_be_completed_before_continuation(self):
        async def runner(**kwargs):
            return {}

        with self.sessions() as db:
            project = GameProject(
                user_id=9,
                title="运行中",
                status="generating",
            )
            db.add(project)
            db.commit()
            project_id = project.id

        module = GenerationRunModule(self.sessions, runner)
        with self.assertRaises(ProjectNotReadyError):
            module.begin(user_id=9, user_input="重复运行", project_id=project_id)

    def test_runner_exception_marks_project_failed(self):
        async def runner(*args, **kwargs):
            raise RuntimeError("runner failed")

        module = GenerationRunModule(self.sessions, runner)
        ticket = module.begin(user_id=10, user_input="生成游戏")
        outcome = asyncio.run(module.execute(ticket))

        self.assertEqual("failed", outcome.status)
        with self.sessions() as db:
            project = db.query(GameProject).one()
            self.assertEqual("failed", project.status)
            error_message = (
                db.query(ChatMessage)
                .filter(ChatMessage.message_type == "error")
                .one()
            )
            self.assertIn("runner failed", error_message.content)

    def test_workflow_error_result_is_not_recorded_as_success(self):
        async def runner(*args, **kwargs):
            return {
                "generated_files": {"index.html": "unchanged"},
                "logs": [],
                "error": "validation failed",
            }

        module = GenerationRunModule(self.sessions, runner)
        ticket = module.begin(user_id=11, user_input="生成游戏")
        outcome = asyncio.run(module.execute(ticket))

        self.assertEqual("failed", outcome.status)
        with self.sessions() as db:
            project = db.query(GameProject).one()
            self.assertEqual("failed", project.status)
            self.assertEqual(
                ["text", "error"],
                [message.message_type for message in db.query(ChatMessage).all()],
            )


if __name__ == "__main__":
    unittest.main()
