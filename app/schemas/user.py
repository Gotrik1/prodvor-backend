from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
