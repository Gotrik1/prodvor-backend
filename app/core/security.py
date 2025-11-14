# app/core/security.py
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.token import TokenPayload


# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, что обычный пароль соответствует хешированному."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Создает хеш из пароля."""
    return pwd_context.hash(password)


# In-memory blacklist for revoked tokens (for dev purposes)
# In production, use a persistent store like Redis.
_BLACKLIST = set()

def add_to_blacklist(jti: str):
    _BLACKLIST.add(jti)

def is_blacklisted(jti: str) -> bool:
    return jti in _BLACKLIST


def create_access_token(subject: str | Any) -> str:
    """
    Создает новый Access-токен.
    :param subject: Идентификатор пользователя (или другие данные), который будет храниться в 'sub'.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4()), # Уникальный идентификатор токена
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any) -> str:
    """
    Создает новый Refresh-токен.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "jti": str(uuid.uuid4()), # Уникальный идентификатор токена
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(
    token: str, 
    secret_key: str, 
    algorithm: str, 
    credentials_exception: Exception
) -> TokenPayload:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        # Check if the token has been revoked
        if is_blacklisted(payload.get("jti")):
            raise credentials_exception
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception
    return token_data

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Декодирует токен, проверяя его подпись и срок жизни.
    Возвращает payload в случае успеха, иначе None.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
