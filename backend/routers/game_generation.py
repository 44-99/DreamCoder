"""
游戏生成API - 提供游戏生成、SSE流式响应等端点
支持统一的新建和继续对话接口
"""
import json

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_db, logger
from core.models import GameProject, GenerationStep, ChatMessage
from core.permission import get_current_user
from workflows.game_gen_workflow import run_game_generation, game_generation_app
from core.knowledge_base import get_template_db


router = APIRouter(prefix="/game", tags=["游戏生成"])


# 请求/响应模型
class GameGenerationRequest(BaseModel):
    project_id: Optional[int] = None  # 项目ID（如果是None，表示新建项目）
    message: str  # 用户需求描述
    title: Optional[str] = None  # 项目标题（仅新建时使用）


class GameGenerationResponse(BaseModel):
    project_id: int
    status: str
    message: str


class GameProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    game_type: Optional[str]
    status: str
    deployment_url: Optional[str]
    quality_score: Optional[float]
    created_at: datetime
    updated_at: datetime


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    message_type: Optional[str]
    extra_data: Optional[dict]
    created_at: datetime


# 统一的对话接口 - 支持新建项目和继续对话
@router.post("/generate", response_model=GameGenerationResponse)
async def generate_game(
    request: GameGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    统一的对话接口：
    - 如果 project_id 为 None：创建新项目并开始生成
    - 如果 project_id 存在：在现有项目上继续添加功能

    后端多智能体自动判断：
    - 如果项目没有代码文件（files 为空或 null）：从零创建游戏
    - 如果项目已有代码文件：基于现有代码改进/添加功能
    """
    try:
        user = current_user["user"]

        # 判断是新建项目还是继续对话
        is_new_project = request.project_id is None
        project = None

        if is_new_project:
            # 创建新项目
            project = GameProject(
                user_id=user.id,
                title=request.title or f"游戏项目-{datetime.now().strftime('%m%d_%H%M')}",
                description=request.message,
                status="generating",
                files=None  # 新项目没有代码文件
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            logger.info(f"创建新项目 {project.id}: {project.title}")

        else:
            # 继续现有项目
            project = db.query(GameProject).filter(
                GameProject.id == request.project_id,
                GameProject.user_id == user.id
            ).first()

            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")

            if project.status != "completed":
                raise HTTPException(
                    status_code=400,
                    detail=f"项目当前状态为 {project.status}，请等待完成后再继续"
                )

            # 更新项目状态和描述
            project.status = "generating"
            project.description = f"{project.description}\n\n用户补充需求: {request.message}"
            project.updated_at = datetime.now(timezone.utc)
            logger.info(f"继续项目 {project.id}: {project.title}")

        # 保存用户消息到聊天记录
        user_message = ChatMessage(
            project_id=project.id,
            role="user",
            content=request.message,
            message_type="text",
            extra_data={"action": "request"}
        )
        db.add(user_message)
        db.commit()

        # 判断是从零创建还是基于现有代码继续
        existing_files = project.files if project.files else None
        is_creating_from_scratch = existing_files is None or len(existing_files) == 0

        # 后台执行生成任务（多智能体自动判断）
        background_tasks.add_task(
            _run_generation_task,
            project_id=project.id,
            user_id=user.id,
            user_input=request.message,
            existing_files=existing_files,
            is_creating_from_scratch=is_creating_from_scratch,
            db=db
        )

        return GameGenerationResponse(
            project_id=project.id,
            status="generating",
            message="创建游戏..." if is_creating_from_scratch else "正在处理您的需求..."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"游戏生成请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_generation_task(
    project_id: int,
    user_id: int,
    user_input: str,
    existing_files: Optional[dict] = None,
    is_creating_from_scratch: bool = True,
    db: Session = None
):
    """
    后台执行生成任务
    - is_creating_from_scratch=True: 从零创建新游戏
    - is_creating_from_scratch=False: 基于现有代码添加功能
    """
    from starlette.concurrency import run_in_threadpool

    start_time = datetime.now()
    mode = "新建" if is_creating_from_scratch else "改进"
    logger.info(f"开始{mode}项目 {project_id}，用户输入: {user_input[:100]}...")

    try:
        # 执行LangGraph工作流
        result = await run_game_generation(user_id, user_input)

        # 更新项目
        project = db.query(GameProject).filter(GameProject.id == project_id).first()
        if not project:
            return

        # 提取结果
        generated_files = result.get('generated_files', {})
        deployment_url = result.get('deployment_url')
        quality_score = result.get('quality_score')
        error = result.get('error')

        # 更新项目信息
        if generated_files:
            project.files = generated_files
        if deployment_url:
            project.deployment_url = deployment_url
        if quality_score is not None:
            project.quality_score = quality_score

        project.game_type = result.get('requirements', {}).get('game_type') or project.game_type
        project.tech_stack = result.get('architecture', {}).get('tech_stack') or project.tech_stack
        project.status = "completed" if not error else "failed"

        # 计算生成时间（累加）
        if project.generation_time:
            project.generation_time += (datetime.now() - start_time).total_seconds()
        else:
            project.generation_time = (datetime.now() - start_time).total_seconds()

        project.updated_at = datetime.now(timezone.utc)

        # 记录生成步骤到 GenerationStep 表
        logs = result.get('logs', [])
        for log in logs:
            step = GenerationStep(
                project_id=project_id,
                step_name=log.get('step'),
                step_type=_map_step_type(log.get('step', '')),
                status=log.get('status'),
                input_data={
                    "user_input": user_input,
                    "mode": mode,
                    "has_existing_files": existing_files is not None
                },
                output_data=log,
                created_at=datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat()))
            )
            db.add(step)

            # 同时保存到聊天消息（作为助手消息）
            assistant_message = ChatMessage(
                project_id=project_id,
                role="assistant",
                content=log.get('message', ''),
                message_type="log",
                extra_data={
                    "step": log.get('step'),
                    "status": log.get('status'),
                    "agent_name": log.get('agent_name'),
                    "tool_name": log.get('tool_name'),
                    "mode": mode
                }
            )
            db.add(assistant_message)

        # 添加最终完成消息
        completion_message = f"✅ {mode}完成！"
        if deployment_url:
            completion_message += " 游戏已部署，可以在预览中查看。"
        if quality_score:
            completion_message += f" 代码质量评分: {quality_score:.1f}/100"

        final_message = ChatMessage(
            project_id=project_id,
            role="assistant",
            content=completion_message,
            message_type="success",
            extra_data={
                "deployment_url": deployment_url,
                "quality_score": quality_score,
                "mode": mode
            }
        )
        db.add(final_message)

        db.commit()
        logger.info(f"项目 {project_id} {mode}完成，耗时: {(datetime.now() - start_time).total_seconds():.1f}秒")

    except Exception as e:
        logger.error(f"生成任务执行失败: {e}", exc_info=True)

        # 标记项目失败
        project = db.query(GameProject).filter(GameProject.id == project_id).first()
        if project:
            project.status = "failed"
            project.updated_at = datetime.now(timezone.utc)

            # 添加错误消息到聊天
            error_message = ChatMessage(
                project_id=project_id,
                role="assistant",
                content=f"❌ {mode}失败：{str(e)}",
                message_type="error",
                extra_data={"error": str(e)}
            )
            db.add(error_message)
            db.commit()


def _map_step_type(step_name: str) -> str:
    """映射步骤类型"""
    step_map = {
        "requirement_analyzer": "analysis",
        "architect_designer": "design",
        "code_generator": "coding",
        "test_validator": "testing",
        "deployment": "deployment"
    }
    return step_map.get(step_name, "other")


# 获取项目列表
@router.get("/projects", response_model=list[GameProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取用户的游戏项目列表"""
    try:
        user = current_user["user"]
        projects = db.query(GameProject).filter(
            GameProject.user_id == user.id
        ).order_by(GameProject.created_at.desc()).all()
        return [
            GameProjectResponse(
                id=p.id,
                title=p.title,
                description=p.description or "",
                game_type=p.game_type,
                status=p.status,
                deployment_url=p.deployment_url,
                quality_score=p.quality_score,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in projects
        ]

    except Exception as e:
        logger.error(f"获取项目列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 获取单个项目详情
@router.get("/projects/{project_id}", response_model=GameProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取项目详情"""
    try:
        user = current_user["user"]
        project = db.query(GameProject).filter(
            GameProject.id == project_id,
            GameProject.user_id == user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        return GameProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description or "",
            game_type=project.game_type,
            status=project.status,
            deployment_url=project.deployment_url,
            quality_score=project.quality_score,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 获取项目文件
@router.get("/projects/{project_id}/files")
async def get_project_files(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取项目的所有文件内容"""
    try:
        user = current_user["user"]
        project = db.query(GameProject).filter(
            GameProject.id == project_id,
            GameProject.user_id == user.id
        ).first()

        if not project:
            logger.error(f"项目 {project_id} 不存在或无权访问")
            raise HTTPException(status_code=404, detail="项目不存在")

        files_dict = project.files or {}
        return {
            "files": files_dict,
            "deployment_url": project.deployment_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# 获取项目生成日志
@router.get("/projects/{project_id}/logs")
async def get_project_logs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取项目生成日志"""
    try:
        user = current_user["user"]
        project = db.query(GameProject).filter(
            GameProject.id == project_id,
            GameProject.user_id == user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        logs = db.query(GenerationStep).filter(
            GenerationStep.project_id == project_id
        ).order_by(GenerationStep.created_at.asc()).all()

        return {
            "project_id": project_id,
            "logs": [
                {
                    "step": log.step_name,
                    "type": log.step_type,
                    "status": log.status,
                    "message": log.output_data.get('message') if log.output_data else '',
                    "timestamp": log.created_at.isoformat()
                }
                for log in logs
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 获取游戏模板列表
@router.get("/templates")
async def get_templates():
    """获取所有游戏模板"""
    try:
        template_db = get_template_db()
        await template_db.initialize()
        templates = template_db.get_all_templates()

        return {
            "templates": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "description": t["description"],
                    "game_type": t["game_type"],
                    "tech_stack": t["tech_stack"],
                    "keywords": t["keywords"]
                }
                for t in templates
            ]
        }

    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 搜索游戏模板
@router.get("/templates/search")
async def search_templates(query: str, top_k: int = 3):
    """搜索游戏模板"""
    try:
        template_db = get_template_db()
        await template_db.initialize()

        templates = await template_db.search_templates(query, top_k=top_k)

        return {
            "query": query,
            "templates": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "description": t["description"],
                    "game_type": t["game_type"],
                    "tech_stack": t["tech_stack"]
                }
                for t in templates
            ]
        }

    except Exception as e:
        logger.error(f"搜索模板失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SSE流式响应 - 实时推送生成进度
@router.get("/generate/stream")
async def generate_game_stream(
    description: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """流式生成游戏 - SSE实时推送进度"""

    async def event_stream():
        try:
            user = current_user["user"]

            # 创建项目
            project = GameProject(
                user_id=user.id,
                title=f"游戏-{datetime.now().strftime('%H%M%S')}",
                description=description,
                status="generating"
            )
            db.add(project)
            db.commit()
            db.refresh(project)

            # 发送项目ID
            yield f"event: project_created\ndata: {json.dumps({'project_id': project.id, 'title': project.title})}\n\n"

            # 执行生成
            result = await run_game_generation(user.id, description)

            # 流式发送日志
            logs = result.get('logs', [])
            for log in logs:
                yield f"event: step_update\ndata: {json.dumps(log)}\n\n"

            # 更新并完成
            project.status = "completed" if not result.get('error') else "failed"
            project.deployment_url = result.get('deployment_url')
            project.quality_score = result.get('quality_score')
            db.commit()

            yield f"event: generation_complete\ndata: {json.dumps({'project_id': project.id, 'status': project.status, 'deployment_url': project.deployment_url})}\n\n"

        except Exception as e:
            logger.error(f"SSE流式生成失败: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


game_router = router


# 删除项目
@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """永久删除项目及其所有相关数据"""
    try:
        user = current_user["user"]

        # 检查项目是否存在且属于该用户
        project = db.query(GameProject).filter(
            GameProject.id == project_id,
            GameProject.user_id == user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 删除项目的聊天消息
        db.query(ChatMessage).filter(ChatMessage.project_id == project_id).delete()

        # 删除项目的生成步骤日志
        db.query(GenerationStep).filter(GenerationStep.project_id == project_id).delete()

        # 删除项目
        db.delete(project)
        db.commit()

        return {"status": "success", "message": "项目已永久删除"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除项目失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/projects/{project_id}/chat", response_model=List[ChatMessageResponse])
async def get_project_chat(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取项目的聊天消息历史"""
    try:
        user = current_user["user"]
        # 验证项目所有权
        project = db.query(GameProject).filter(
            GameProject.id == project_id,
            GameProject.user_id == user.id
        ).first()

        if not project:
            logger.error(f"项目 {project_id} 不存在或无权访问")
            raise HTTPException(status_code=404, detail="项目不存在")

        # 获取聊天消息
        messages = db.query(ChatMessage).filter(
            ChatMessage.project_id == project_id
        ).order_by(ChatMessage.created_at.asc()).all()
        return [
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                message_type=msg.message_type,
                extra_data=msg.extra_data,
                created_at=msg.created_at
            )
            for msg in messages
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天消息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

