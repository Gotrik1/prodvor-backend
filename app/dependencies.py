from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.core.config import settings
from app.crud import user
from app.models import User

class TokenData(BaseModel):
    sub: str | None = None

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"/api/v1/login/access-token")

async def get_db():
    async with SessionLocal() as session:
        yield session

def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)):
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
    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    db_user = user.get(db, id=token_data.sub)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
