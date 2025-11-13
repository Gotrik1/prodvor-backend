# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
import uuid

from app.schemas.token import TokenPayload

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# In-memory blacklist for revoked tokens (for dev purposes)
# In production, use a persistent store like Redis.
_BLACKLIST = set()

def add_to_blacklist(jti: str):
    _BLACKLIST.add(jti)

def is_blacklisted(jti: str) -> bool:
    return jti in _BLACKLIST


# JWT Token Creation and Verification
def create_access_token(
    subject: Any, 
    secret_key: str, 
    algorithm: str, 
    expires_delta: timedelta
) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def create_refresh_token(
    subject: Any, 
    secret_key: str, 
    algorithm: str, 
    expires_delta: timedelta
) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
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
