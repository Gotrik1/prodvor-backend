from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Argon2 для новых паролей, но поддержка bcrypt для старых
# 'bcrypt' должен быть в 'schemes' для проверки старых хешей
pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли обычный пароль хешированному.
    Использует pwd_context, который поддерживает и bcrypt (для старых паролей)
    и argon2 (для новых).
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Хеширует пароль для сохранения в базе данных.
    Использует argon2 как схему по умолчанию.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": to_encode.get("identity")})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        identity = payload.get("sub")
        if identity is None:
            raise credentials_exception
        return identity
    except JWTError:
        raise credentials_exception
