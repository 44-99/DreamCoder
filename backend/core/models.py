from datetime import datetime, timezone

from core.dependencies import Base
from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy import Text, DateTime, ForeignKey, Float, LargeBinary


# 用户表
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(50))
    avatar = Column(String(200))
    is_active = Column(Boolean, default=True, nullable=False)


# 游戏生成项目表
class GameProject(Base):
    __tablename__ = 'game_projects'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    game_type = Column(String(50))
    tech_stack = Column(String(50))
    status = Column(String(40), default='generating', nullable=False)  # generating, completed, failed
    files = Column(JSON)  # 存储生成的文件结构
    deployment_url = Column(String(300))
    quality_score = Column(Float)
    generation_time = Column(Float)
    langsmith_run_id = Column(String(100))
    metadata_ = Column('metadata', JSON)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


# 游戏生成步骤日志
class GenerationStep(Base):
    __tablename__ = 'generation_steps'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('game_projects.id'), nullable=False, index=True)
    step_name = Column(String(100), nullable=False)
    step_type = Column(String(50))  # analysis, design, coding, testing, deployment
    status = Column(String(40), default='pending', nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    duration = Column(Float)
    langsmith_trace_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))


# RAG游戏模板表
class GameTemplate(Base):
    __tablename__ = 'game_templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    game_type = Column(String(50))
    tech_stack = Column(String(50))
    mechanics = Column(JSON)
    file_structure = Column(JSON)
    reference_code = Column(Text)
    vector_embedding = Column(LargeBinary)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))


# 会话消息表 - 用于多轮对话
class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('game_projects.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_type = Column(String(50))  # 'text', 'log', 'error', 'success', 'code_update'
    extra_data = Column(JSON)  # 额外信息，如agent_name, tool_name等
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

