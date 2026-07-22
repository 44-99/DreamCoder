"""
游戏生成API - 提供游戏生成、SSE流式响应等端点
支持统一的新建和继续对话接口
"""
import json

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_db, logger
from core.models import GameProject, GenerationStep, ChatMessage
from core.permission import get_current_user
from core.knowledge_base import get_template_db
from modules.generation_run import (
    ProjectNotFoundError,
    ProjectNotReadyError,
    generation_run_module,
)


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

        ticket = generation_run_module.begin(
            user_id=user.id,
            user_input=request.message,
            project_id=request.project_id,
            title=request.title,
        )

        # 后台执行生成任务（多智能体自动判断）
        background_tasks.add_task(
            generation_run_module.execute,
            ticket,
        )

        return GameGenerationResponse(
            project_id=ticket.project_id,
            status="generating",
            message="创建游戏..." if ticket.is_creating_from_scratch else "正在处理您的需求..."
        )

    except ProjectNotFoundError:
        raise HTTPException(status_code=404, detail="项目不存在")
    except ProjectNotReadyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"游戏生成请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    current_user: dict = Depends(get_current_user)
):
    """流式生成游戏 - SSE实时推送进度"""
    user = current_user["user"]
    ticket = generation_run_module.begin(
        user_id=user.id,
        user_input=description,
        title=f"游戏-{datetime.now().strftime('%H%M%S')}",
    )

    async def event_stream():
        try:
            # 发送项目ID
            yield f"event: project_created\ndata: {json.dumps({'project_id': ticket.project_id, 'title': ticket.title})}\n\n"

            # 执行生成
            outcome = await generation_run_module.execute(ticket)

            # 流式发送日志
            for log in outcome.logs:
                yield f"event: step_update\ndata: {json.dumps(log)}\n\n"

            yield f"event: generation_complete\ndata: {json.dumps({'project_id': outcome.project_id, 'status': outcome.status, 'deployment_url': outcome.deployment_url})}\n\n"

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

