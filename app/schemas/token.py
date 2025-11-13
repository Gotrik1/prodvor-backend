from pydantic import BaseModel, Field
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int
    jti: str
    iss: Optional[str] = None
    aud: Optional[str] = None
    scope: Optional[List[str]] = Field(default=None)

TokenData = TokenPayload

class Msg(BaseModel):
    msg: str
