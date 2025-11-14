from typing import AsyncGenerator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

class Pagination:
    def __init__(self, offset: int = 0, limit: int = 20):
        self.offset = offset
        self.limit = limit

def get_pagination(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> Pagination:
    return Pagination(offset=offset, limit=limit)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
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

    if token_data.sub is None:
        raise credentials_exception

    try:
        user_id = UUID(token_data.sub)
    except ValueError:
        raise credentials_exception

    user = await crud.user.get(db, id=user_id)
    if not user:
        raise credentials_exception
        
    return user
