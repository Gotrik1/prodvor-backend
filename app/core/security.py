
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 1. Используем ТОЛЬКО bcrypt для полной совместимости с legacy-системой.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль, используя только bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширует пароль, используя только bcrypt."""
    return pwd_context.hash(password)

def create_access_token(identity: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен, 1:1 совместимый с legacy-системой.
    - Дублирует identity в sub для надежности.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "identity": identity,
        "sub": identity, # 2. Дублируем identity в sub для совместимости.
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception) -> Any:
    """
    Проверяет JWT токен, ищет claim 'identity' или 'sub'.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        # Пытаемся получить identity, если нет, то sub, как в legacy.
        identity = payload.get("identity") or payload.get("sub")
        if identity is None:
            raise credentials_exception
        return identity
    except JWTError:
        raise credentials_exception
