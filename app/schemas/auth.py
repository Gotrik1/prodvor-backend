from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegistration(BaseModel):
    email: EmailStr
    nickname: str
    password: str
    role: str = 'player'
    city: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class TokenPayload(BaseModel):
    sub: str # This will be the user ID
