from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.core.config import settings
from app.crud import user
from app.models import User
from app.utils.security import is_blacklisted

class TokenData(BaseModel):
    sub: str | None = None
    jti: str | None = None

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if token_data.sub is None or token_data.jti is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if is_blacklisted(token_data.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    db_user = await user.get(db, id=token_data.sub)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

async def get_current_user_from_refresh_token(db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, refresh token invalid or expired",
        )
    if token_data.sub is None or token_data.jti is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, refresh token invalid or expired",
        )
    if is_blacklisted(token_data.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    db_user = await user.get(db, id=token_data.sub)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
