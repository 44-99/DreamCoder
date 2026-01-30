import asyncio
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from core.dependencies import engine
from core.models import Base
from routers import auth, user, game_generation

sys.path.append(str(Path(__file__).parent.parent))

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DreamCoder", description="基于LangGraph的游戏生成系统", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"], )
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def health_check():
    return {"status": "running", "timestamp": datetime.now(), "service": "DreamCoder - AI游戏生成系统"}


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(game_generation.router)
