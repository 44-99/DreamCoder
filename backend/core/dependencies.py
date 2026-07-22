"""Shared configuration and infrastructure adapters."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import quote_plus

from dotenv import dotenv_values, load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.verification_store import (
    VerificationCodeStore,
    memory_verification_store,
)

# Load .env from backend/ directory if present
_here = Path(__file__).parent.parent
_env_path = _here / '.env'
if _env_path.exists():
    # 使用 override=True 确保覆盖已存在的环境变量
    load_dotenv(dotenv_path=_env_path, override=True)

    # 同时直接读取并设置所有环境变量，确保最新值生效
    env_values = dotenv_values(_env_path)
    for key, value in env_values.items():
        if value is not None:
            os.environ[key] = value

# Database: SQLite by default; set DATABASE_URL for PostgreSQL in hosted deployments.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dreamcoder")

encoded_password = quote_plus(DB_PASSWORD)
legacy_postgres_url = (
    f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}?client_encoding=utf8"
)
default_database_url = (
    legacy_postgres_url
    if any(os.getenv(key) for key in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"))
    else f"sqlite:///{(_here / 'dreamcoder.db').as_posix()}"
)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    default_database_url,
)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_options: dict[str, Any] = {
        "connect_args": {"check_same_thread": False},
    }
else:
    engine_options = {
        "pool_pre_ping": True,
        "connect_args": {"options": "-c client_encoding=utf8"},
    }

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis is optional. Local development uses the in-memory verification store.
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() in {"1", "true", "yes"}
REDIS_REQUIRED = os.getenv("REDIS_REQUIRED", "false").lower() in {"1", "true", "yes"}


def _create_redis_client():
    try:
        import redis
    except ImportError:
        if REDIS_REQUIRED:
            raise RuntimeError(
                "Redis is required but the redis package is not installed. "
                "Install backend/requirements-optional.txt."
            )
        return None

    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
        max_connections=20,
        retry_on_timeout=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )
    try:
        client.ping()
        return client
    except Exception as exc:
        if REDIS_REQUIRED:
            raise RuntimeError("Redis is required but unavailable") from exc
        logging.getLogger(__name__).warning(
            "Redis unavailable; using the process-local verification store: %s",
            exc,
        )
        return None


_redis_client = _create_redis_client() if REDIS_ENABLED else None


def get_verification_store() -> Iterator[VerificationCodeStore]:
    yield _redis_client or memory_verification_store


def publish_event(session_id: int, event: dict, redis_client=None) -> None:
    """发布事件到Redis频道"""
    client = redis_client or _redis_client
    if client is None:
        return
    try:
        channel = f"session:{session_id}:events"
        payload = json.dumps(event, ensure_ascii=False, default=str)
        client.publish(channel, payload)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"publish_event failed: {e}")


# JWT 和密码哈希配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Resolve data directories relative to backend/, not the caller's current directory.
PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", str(_here / "static" / "projects")))
CHROMA_DB_DIR = Path(os.getenv("CHROMA_DB_DIR", str(_here / "data" / "chroma_db")))
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
os.environ["PROJECTS_DIR"] = str(PROJECTS_DIR)
os.environ["CHROMA_DB_DIR"] = str(CHROMA_DB_DIR)
