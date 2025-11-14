# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core import security
from app.core.config import settings

class AuthService:
    async def authenticate_user(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[models.User]:
        """Аутентифицирует пользователя."""
        user = await crud.user.get_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(
        self, db: AsyncSession, *, user_in: schemas.user.UserCreate
    ) -> Optional[models.User]:
        """Регистрирует нового пользователя."""
        user = await crud.user.get_by_email(db, email=user_in.email)
        if user:
            return None
        
        user_in.password = security.get_password_hash(user_in.password)
        user_create = schemas.user.UserCreateDB(**user_in.dict())
        user = await crud.user.create(db, obj_in=user_create)
        return user

    async def create_session(
        self, db: AsyncSession, *, user_id: UUID, user_agent: Optional[str], ip_address: Optional[str]
    ) -> Tuple[str, str]:
        """
        Создает новую сессию, генерирует и возвращает пару токенов.
        """
        access_token = security.create_access_token(user_id)
        refresh_token = security.create_refresh_token(user_id)
        
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        
        session_in = schemas.session.SessionCreate(
            user_id=user_id,
            refresh_token=refresh_token, # Храним сам токен
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        await crud.session.create(db, obj_in=session_in)
        
        return access_token, refresh_token

    async def refresh_session(
        self, db: AsyncSession, *, old_refresh_token: str, user_agent: Optional[str], ip_address: Optional[str]
    ) -> Optional[Tuple[str, str]]:
        """
        Обновляет сессию (ротация refresh-токена).
        """
        payload = security.decode_token(old_refresh_token)
        if not payload:
            return None # Невалидный токен

        session = await crud.session.get_by_refresh_token(db, refresh_token=old_refresh_token)
        if not session or session.expires_at < datetime.now(timezone.utc):
            if session: # Если сессия есть, но просрочена, удаляем ее
                await crud.session.remove(db, id=session.id)
            return None # Сессия не найдена или просрочена
            
        # Удаляем старую сессию
        await crud.session.remove(db, id=session.id)
        
        # Создаем новую сессию и токены
        return await self.create_session(
            db, user_id=session.user_id, user_agent=user_agent, ip_address=ip_address
        )

    async def revoke_session(self, db: AsyncSession, *, refresh_token: str) -> bool:
        """
        Отозвать сессию (logout).
        """
        session = await crud.session.get_by_refresh_token(db, refresh_token=refresh_token)
        if not session:
            return False # Сессия не найдена
        
        await crud.session.remove(db, id=session.id)
        return True

auth_service = AuthService()
