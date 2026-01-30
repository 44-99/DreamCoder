# DreamCoder v2.0 配置
import os
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

# Load .env from backend/ directory if present
_here = Path(__file__).parent.parent
_env_path = _here / '.env'
if _env_path.exists():
    # 使用 override=True 确保覆盖已存在的环境变量
    load_dotenv(dotenv_path=_env_path, override=True)

    # 同时直接读取并设置所有环境变量，确保最新值生效
    env_values = dotenv_values(_env_path)
    for key, value in env_values.items():
        os.environ[key] = value

import json
import logging
from urllib.parse import quote_plus

import redis
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL 配置
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "dreamcoder")

encoded_password = quote_plus(DB_PASSWORD)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, connect_args={"options": "-c client_encoding=utf8"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    max_connections=20,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30
)


def get_redis():
    try:
        redis_client = redis.Redis(connection_pool=redis_pool)
        try:
            redis_client.ping()
        except Exception as e:
            logging.getLogger(__name__).warning(f"Redis ping failed: {e}")
            yield None
            return
        yield redis_client
    except Exception as e:
        logging.getLogger(__name__).warning(f"get_redis failed: {e}")
        yield None
    finally:
        pass


def publish_event(session_id: int, event: dict, redis_client: redis.Redis | None = None) -> None:
    """发布事件到Redis频道"""
    try:
        r = redis_client if redis_client is not None else redis.Redis(connection_pool=redis_pool)
        channel = f"session:{session_id}:events"
        payload = json.dumps(event, ensure_ascii=False, default=str)
        r.publish(channel, payload)
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

# 确保必要的目录存在
os.makedirs(os.getenv("PROJECTS_DIR", "./generated_projects"), exist_ok=True)
os.makedirs("./data/chroma_db", exist_ok=True)
