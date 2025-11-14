
from pydantic import BaseModel
from typing import Optional
import uuid


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Msg(BaseModel):
    msg: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Единая и правильная модель для данных токена
class TokenPayload(BaseModel):
    sub: Optional[uuid.UUID] = None
    jti: Optional[str] = None
