"""Deep module for the complete game generation lifecycle."""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional
from uuid import uuid4

from sqlalchemy.orm import Session, sessionmaker

from core.dependencies import SessionLocal, logger
from core.models import ChatMessage, GameProject, GenerationStep


WorkflowRunner = Callable[..., Awaitable[Dict[str, Any]]]


class ProjectNotFoundError(Exception):
    """The requested project does not exist or is not owned by the user."""


class ProjectNotReadyError(Exception):
    """The requested project cannot start another generation run yet."""

    def __init__(self, status: str):
        self.status = status
        super().__init__(f"项目当前状态为 {status}，请等待完成后再继续")


@dataclass(frozen=True)
class GenerationRunTicket:
    project_id: int
    user_id: int
    user_input: str
    existing_files: Dict[str, str]
    is_creating_from_scratch: bool
    thread_id: str
    title: str

    @property
    def mode(self) -> str:
        return "新建" if self.is_creating_from_scratch else "改进"


@dataclass(frozen=True)
class GenerationRunOutcome:
    project_id: int
    status: str
    deployment_url: Optional[str]
    quality_score: Optional[float]
    logs: list[Dict[str, Any]]
    error: Optional[str] = None


class GenerationRunModule:
    """Own project state, workflow execution, persistence, and run completion."""

    def __init__(
        self,
        session_factory: sessionmaker = SessionLocal,
        workflow_runner: Optional[WorkflowRunner] = None,
    ) -> None:
        self._session_factory = session_factory
        self._workflow_runner = workflow_runner

    def begin(
        self,
        *,
        user_id: int,
        user_input: str,
        project_id: Optional[int] = None,
        title: Optional[str] = None,
    ) -> GenerationRunTicket:
        """Create or reserve a project and persist the user's request atomically."""
        with self._session_factory() as db:
            try:
                if project_id is None:
                    project = GameProject(
                        user_id=user_id,
                        title=title or f"游戏项目-{datetime.now().strftime('%m%d_%H%M')}",
                        description=user_input,
                        status="generating",
                        files=None,
                    )
                    db.add(project)
                    db.flush()
                    existing_files: Dict[str, str] = {}
                    logger.info("创建新项目 %s: %s", project.id, project.title)
                else:
                    project = (
                        db.query(GameProject)
                        .filter(
                            GameProject.id == project_id,
                            GameProject.user_id == user_id,
                        )
                        .with_for_update()
                        .first()
                    )
                    if project is None:
                        raise ProjectNotFoundError("项目不存在")
                    if project.status != "completed":
                        raise ProjectNotReadyError(project.status)

                    existing_files = deepcopy(project.files or {})
                    project.status = "generating"
                    project.description = (
                        f"{project.description or ''}\n\n用户补充需求: {user_input}"
                    ).strip()
                    project.updated_at = datetime.now(timezone.utc)
                    logger.info("继续项目 %s: %s", project.id, project.title)

                db.add(
                    ChatMessage(
                        project_id=project.id,
                        role="user",
                        content=user_input,
                        message_type="text",
                        extra_data={"action": "request"},
                    )
                )
                db.commit()
                db.refresh(project)

                return GenerationRunTicket(
                    project_id=project.id,
                    user_id=user_id,
                    user_input=user_input,
                    existing_files=existing_files,
                    is_creating_from_scratch=not bool(existing_files),
                    thread_id=f"project_{project.id}_{uuid4().hex}",
                    title=project.title,
                )
            except Exception:
                db.rollback()
                raise

    async def execute(self, ticket: GenerationRunTicket) -> GenerationRunOutcome:
        """Run the workflow and close the project lifecycle in an owned Session."""
        started_at = datetime.now(timezone.utc)
        logger.info(
            "开始%s项目 %s，用户输入: %s...",
            ticket.mode,
            ticket.project_id,
            ticket.user_input[:100],
        )

        try:
            workflow_runner = self._workflow_runner
            if workflow_runner is None:
                from workflows.game_gen_workflow import run_game_generation

                workflow_runner = run_game_generation

            result = await workflow_runner(
                ticket.user_id,
                ticket.user_input,
                existing_files=deepcopy(ticket.existing_files) or None,
                thread_id=ticket.thread_id,
            )
            outcome = self._persist_result(ticket, result, started_at)
            logger.info(
                "项目 %s %s结束，状态: %s",
                ticket.project_id,
                ticket.mode,
                outcome.status,
            )
            return outcome
        except Exception as exc:
            logger.error("生成任务执行失败: %s", exc, exc_info=True)
            self._record_execution_failure(ticket, str(exc))
            return GenerationRunOutcome(
                project_id=ticket.project_id,
                status="failed",
                deployment_url=None,
                quality_score=None,
                logs=[],
                error=str(exc),
            )

    def _persist_result(
        self,
        ticket: GenerationRunTicket,
        result: Dict[str, Any],
        started_at: datetime,
    ) -> GenerationRunOutcome:
        generated_files = result.get("generated_files") or {}
        deployment_url = result.get("deployment_url")
        quality_score = result.get("quality_score")
        error = result.get("error")
        logs = result.get("logs") or []
        status = "failed" if error else "completed"

        with self._session_factory() as db:
            try:
                project = self._load_owned_project(db, ticket)
                if generated_files:
                    project.files = generated_files
                if deployment_url:
                    project.deployment_url = deployment_url
                if quality_score is not None:
                    project.quality_score = quality_score

                requirements = result.get("requirements") or {}
                architecture = result.get("architecture") or {}
                project.game_type = requirements.get("game_type") or project.game_type
                project.tech_stack = architecture.get("tech_stack") or project.tech_stack
                project.status = status
                elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
                project.generation_time = (project.generation_time or 0) + elapsed
                project.updated_at = datetime.now(timezone.utc)

                for log in logs:
                    self._add_log_records(db, ticket, log)

                db.add(self._final_message(ticket, error, deployment_url, quality_score))
                db.commit()
            except Exception:
                db.rollback()
                raise

        return GenerationRunOutcome(
            project_id=ticket.project_id,
            status=status,
            deployment_url=deployment_url,
            quality_score=quality_score,
            logs=logs,
            error=error,
        )

    def _load_owned_project(
        self, db: Session, ticket: GenerationRunTicket
    ) -> GameProject:
        project = (
            db.query(GameProject)
            .filter(
                GameProject.id == ticket.project_id,
                GameProject.user_id == ticket.user_id,
            )
            .first()
        )
        if project is None:
            raise ProjectNotFoundError("项目不存在")
        return project

    def _add_log_records(
        self,
        db: Session,
        ticket: GenerationRunTicket,
        log: Dict[str, Any],
    ) -> None:
        step_name = log.get("step") or "unknown"
        db.add(
            GenerationStep(
                project_id=ticket.project_id,
                step_name=step_name,
                step_type=_map_step_type(step_name),
                status=log.get("status") or "unknown",
                input_data={
                    "user_input": ticket.user_input,
                    "mode": ticket.mode,
                    "has_existing_files": bool(ticket.existing_files),
                },
                output_data=log,
                created_at=_parse_timestamp(log.get("timestamp")),
            )
        )
        db.add(
            ChatMessage(
                project_id=ticket.project_id,
                role="assistant",
                content=log.get("message") or "",
                message_type="log",
                extra_data={
                    "step": log.get("step"),
                    "status": log.get("status"),
                    "agent_name": log.get("agent_name"),
                    "tool_name": log.get("tool_name"),
                    "mode": ticket.mode,
                },
            )
        )

    def _final_message(
        self,
        ticket: GenerationRunTicket,
        error: Optional[str],
        deployment_url: Optional[str],
        quality_score: Optional[float],
    ) -> ChatMessage:
        if error:
            return ChatMessage(
                project_id=ticket.project_id,
                role="assistant",
                content=f"❌ {ticket.mode}失败：{error}",
                message_type="error",
                extra_data={"error": error, "mode": ticket.mode},
            )

        content = f"✅ {ticket.mode}完成！"
        if deployment_url:
            content += " 游戏已部署，可以在预览中查看。"
        if quality_score is not None:
            content += f" 代码质量评分: {quality_score:.1f}/100"
        return ChatMessage(
            project_id=ticket.project_id,
            role="assistant",
            content=content,
            message_type="success",
            extra_data={
                "deployment_url": deployment_url,
                "quality_score": quality_score,
                "mode": ticket.mode,
            },
        )

    def _record_execution_failure(
        self, ticket: GenerationRunTicket, error: str
    ) -> None:
        try:
            with self._session_factory() as db:
                project = self._load_owned_project(db, ticket)
                project.status = "failed"
                project.updated_at = datetime.now(timezone.utc)
                db.add(self._final_message(ticket, error, None, None))
                db.commit()
        except Exception as persistence_error:
            logger.error(
                "项目 %s 的失败状态无法持久化: %s",
                ticket.project_id,
                persistence_error,
                exc_info=True,
            )


def _map_step_type(step_name: str) -> str:
    return {
        "requirement_analyzer": "analysis",
        "architect_designer": "design",
        "code_generator": "coding",
        "test_validator": "testing",
        "deployment": "deployment",
    }.get(step_name, "other")


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)


generation_run_module = GenerationRunModule()
