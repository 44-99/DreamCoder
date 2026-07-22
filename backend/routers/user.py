import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from jose import jwt
from sqlalchemy.orm import Session

from core.dependencies import (
    ALGORITHM,
    SECRET_KEY,
    get_db,
    get_verification_store,
    logger,
    pwd_context,
)
from core.models import User
from core.permission import get_current_user
from core.verification_store import VerificationCodeStore

router = APIRouter(prefix="/user", tags=["用户信息"])

AVATAR_DIR = Path(
    os.getenv(
        "AVATAR_DIR",
        str(Path(__file__).resolve().parents[1] / "static" / "avatars"),
    )
)
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


@router.patch("/avatar")
async def update_avatar(avatar: UploadFile = File(..., description="用户头像文件"), db: Session = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or not current_user["user"]:
            raise HTTPException(status_code=400, detail="用户未登录")
        user = current_user["user"]
        file_ext = os.path.splitext(avatar.filename)[1].lower()
        if file_ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            raise HTTPException(status_code=400, detail="仅支持 PNG、JPG、JPEG 或 GIF 格式")
        # 检查用户是否已有头像，并删除旧头像文件
        if user.avatar:
            if isinstance(user.avatar, UploadFile):
                old_avatar_filename = os.path.basename(user.avatar.filename)
            else:
                old_avatar_filename = os.path.basename(str(user.avatar))
            old_avatar_path = AVATAR_DIR / old_avatar_filename
            if old_avatar_path.exists():
                old_avatar_path.unlink()
        # 保存新头像
        avatar_filename = f"user_{user.id}{file_ext}"
        avatar_path = AVATAR_DIR / avatar_filename
        with avatar_path.open("wb") as buffer:
            buffer.write(await avatar.read())
        user.avatar = f"/{AVATAR_DIR}/{avatar_filename}"
        db.commit()
        return {"status": "success", "avatar": user.avatar}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/username")
def update_username(new_username: str = Body(..., description="新用户名"), db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or not current_user["user"]:
            raise HTTPException(status_code=400, detail="用户名不存在")
        user = current_user["user"]
        if db.query(User).filter(User.username == new_username).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        if user.avatar:
            file_ext = Path(user.avatar).suffix.lower()
            if file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                old_avatar_path = AVATAR_DIR / f"user_{user.username}{file_ext}"
                if old_avatar_path.exists():
                    new_avatar_path = AVATAR_DIR / f"user_{new_username}{file_ext}"
                    old_avatar_path.rename(new_avatar_path)
                    user.avatar = f"/{AVATAR_DIR}/user_{new_username}{file_ext}"
        user.username = new_username
        db.commit()
        payload = {
            "id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        new_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"status": "success", "new_token": new_token,
                "user": {"id": user.id, "username": new_username, "phone": user.phone,
                         "email": user.email, "avatar": user.avatar}}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/phone")
def verify_and_update_phone(new_phone: str = Body(..., description="新邮箱"),
                            code: str = Body(..., description="验证码"), db: Session = Depends(get_db),
                            verification_store: VerificationCodeStore = Depends(get_verification_store),
                            current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or not current_user["user"]:
            raise HTTPException(status_code=400, detail="用户名不存在")
        stored_code = verification_store.get(f"verification_code:{new_phone}")
        if not stored_code or stored_code != code:
            raise HTTPException(status_code=400, detail="验证码无效或已过期")
        current_user["user"].phone = new_phone
        db.commit()
        verification_store.delete(f"verification_code:{new_phone}")
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/email")
def verify_and_update_email(new_email: str = Body(..., description="新邮箱"),
                            code: str = Body(..., description="验证码"), db: Session = Depends(get_db),
                            verification_store: VerificationCodeStore = Depends(get_verification_store),
                            current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or not current_user["user"]:
            raise HTTPException(status_code=400, detail="用户名不存在")
        stored_code = verification_store.get(f"verification_code:{new_email}")
        if not stored_code or stored_code != code:
            raise HTTPException(status_code=400, detail="验证码无效或已过期")
        current_user["user"].email = new_email
        db.commit()
        logger.info(f"用户{current_user['user'].username}更新了邮箱为{new_email}")
        verification_store.delete(f"verification_code:{new_email}")
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/password")
def update_password(current_password: str = Body(..., description="当前密码"),
                    new_password: str = Body(..., description="新密码"), db: Session = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    try:
        if not current_user or not current_user["user"]:
            raise HTTPException(status_code=400, detail="用户名不存在")
        user = current_user["user"]
        if not pwd_context.verify(current_password, str(user.hashed_password)):
            raise HTTPException(status_code=400, detail="当前密码错误")
        user.hashed_password = pwd_context.hash(new_password)
        db.commit()
        return {"status": "success"}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
