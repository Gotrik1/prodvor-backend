from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
import uuid
from datetime import date, datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[date] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

class ProfileButton(BaseModel):
    action: Dict[str, Any]
    text: str

class UserProfile(User):
    profile_buttons: List[ProfileButton] = []
