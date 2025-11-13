from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app import crud, models
from app.db.session import SessionLocal
from app.core import security
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class Pagination(BaseModel):
    limit: int
    offset: int

def get_pagination(
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items offset"),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = security.verify_token(
        token=token,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        credentials_exception=credentials_exception
    )

    user = await crud.user.get(db, id=token_data.sub)
    if user is None:
        raise credentials_exception
    return user
