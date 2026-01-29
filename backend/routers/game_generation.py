"""
游戏生成API - 提供游戏生成、SSE流式响应等端点
"""
import os
import json
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.dependencies import get_db, logger
from core.models import User, GameProject, GenerationStep
from core.permission import get_current_user
from workflows.game_gen_workflow import run_game_generation, game_generation_app
from core.knowledge_base import get_template_db


router = APIRouter(prefix="/game", tags=["游戏生成"])


# 请求/响应模型
class GameGenerationRequest(BaseModel):
    description: str  # 用户描述
    title: Optional[str] = None  # 项目标题


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


# 生成游戏项目
@router.post("/generate", response_model=GameGenerationResponse)
async def generate_game(
    request: GameGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """生成游戏项目"""
    try:
        user = current_user["user"]

        # 创建项目记录
        project = GameProject(
            user_id=user.id,
            title=request.title or f"游戏项目-{datetime.now().strftime('%m%d_%H%M')}",
            description=request.description,
            status="generating"
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # 后台执行生成任务
        background_tasks.add_task(
            _run_generation_task,
            project_id=project.id,
            user_id=user.id,
            user_input=request.description,
            db=db
        )

        return GameGenerationResponse(
            project_id=project.id,
            status="generating",
            message="游戏生成中..."
        )

    except Exception as e:
        logger.error(f"游戏生成请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_generation_task(project_id: int, user_id: int, user_input: str, db: Session):
    """后台执行生成任务"""
    from starlette.concurrency import run_in_threadpool

    start_time = datetime.now()

    try:
        # 执行LangGraph工作流
        result = await run_game_generation(user_id, user_input)

        # 更新项目
        project = db.query(GameProject).filter(GameProject.id == project_id).first()
        if not project:
            return

        # 提取结果
        requirements = result.get('requirements', {})
        architecture = result.get('architecture', {})
        generated_files = result.get('generated_files', {})
        test_results = result.get('test_results', [])
        deployment_url = result.get('deployment_url')
        quality_score = result.get('quality_score')
        error = result.get('error')

        # 更新项目信息
        project.game_type = requirements.get('game_type')
        project.tech_stack = architecture.get('tech_stack')
        project.files = generated_files
        project.deployment_url = deployment_url
        project.quality_score = quality_score
        project.status = "completed" if not error else "failed"
        project.generation_time = (datetime.now() - start_time).total_seconds()

        # 记录生成步骤
        logs = result.get('logs', [])
        for log in logs:
            step = GenerationStep(
                project_id=project_id,
                step_name=log.get('step'),
                step_type=_map_step_type(log.get('step', '')),
                status=log.get('status'),
                input_data={"user_input": user_input},
                output_data=log,
                created_at=datetime.fromisoformat(log.get('timestamp', datetime.now().isoformat()))
            )
            db.add(step)

        db.commit()

        logger.info(f"项目 {project_id} 生成完成，耗时: {project.generation_time}秒")

    except Exception as e:
        logger.error(f"生成任务执行失败: {e}")
        project = db.query(GameProject).filter(GameProject.id == project_id).first()
        if project:
            project.status = "failed"
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
        ).order_by(GameProject.created_at.desc()).limit(20).all()

        return [
            GameProjectResponse(
                id=p.id,
                title=p.title,
                description=p.description or "",
                game_type=p.game_type,
                status=p.status,
                deployment_url=p.deployment_url,
                quality_score=p.quality_score,
                created_at=p.created_at
            )
            for p in projects
        ]

    except Exception as e:
        logger.error(f"获取项目列表失败: {e}")
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
            created_at=project.created_at
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
            raise HTTPException(status_code=404, detail="项目不存在")

        return {
            "files": project.files or {},
            "deployment_url": project.deployment_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目文件失败: {e}")
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
