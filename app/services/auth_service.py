# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
import uuid
from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.core.config import settings
from app.schemas.session import SessionCreate
from app.schemas.user import UserCreate, UserCreateDB

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return crypt_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return crypt_context.hash(password)

    async def register_user(self, db: AsyncSession, *, user_in: UserCreate) -> models.User:
        user = await crud.user.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_create_db = UserCreateDB(
            email=user_in.email,
            password=self.get_password_hash(user_in.password),
            nickname=user_in.nickname,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            birth_date=user_in.birth_date,
        )
        user = await crud.user.create(db, obj_in=user_create_db)
        return user

    async def authenticate_user(self, db: AsyncSession, *, email: str, password: str) -> models.User | None:
        user = await crud.user.get_by_email(db, email=email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_session(self, db: AsyncSession, *, user_id: str, user_agent: str, ip_address: str) -> tuple[str, str]:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(data={"sub": str(user_id)}, expires_delta=access_token_expires)

        refresh_token_expires_days = settings.REFRESH_TOKEN_EXPIRE_MINUTES
        refresh_token = self.create_refresh_token(data={"sub": str(user_id)}, expires_in_days=refresh_token_expires_days)

        session_in = SessionCreate(
            user_id=user_id,
            refresh_token=refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=refresh_token_expires_days)
        )

        await crud.session.create(db, obj_in=session_in)

        return access_token, refresh_token

    def create_refresh_token(self, data: dict, expires_in_days: int) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def refresh_session(self, db: AsyncSession, *, refresh_token: str, user_agent: str, ip_address: str) -> tuple[str, str]:
        session = await self.validate_refresh_token(db, refresh_token)
        if not session:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        await crud.session.remove(db, id=session.id)
        
        return await self.create_session(db, user_id=session.user_id, user_agent=user_agent, ip_address=ip_address)

    async def validate_refresh_token(self, db: AsyncSession, token: str) -> models.Session | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None

        session = await crud.session.get_by_refresh_token(db, refresh_token=token)
        if not session or session.expires_at < datetime.now(timezone.utc):
            return None

        return session

    async def logout(self, db: AsyncSession, *, refresh_token: str) -> None:
        session = await crud.session.get_by_refresh_token(db, refresh_token=refresh_token)
        if session:
            await crud.session.remove(db, id=session.id)

auth_service = AuthService()