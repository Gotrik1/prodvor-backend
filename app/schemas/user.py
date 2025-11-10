from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime

class PlayerProfileBase(BaseModel):
    matchesPlayed: int = 0
    wins: int = 0
    goals: int = 0
    assists: int = 0
    mvpAwards: int = 0
    elo: int = 1200

class PlayerProfile(PlayerProfileBase):
    pass

class RefereeProfileBase(BaseModel):
    category: Optional[str] = None
    matchesJudged: int = 0

class RefereeProfile(RefereeProfileBase):
    pass

class CoachProfileBase(BaseModel):
    specialization: Optional[str] = None
    experienceYears: Optional[int] = None

class CoachProfile(CoachProfileBase):
    pass

class UserBase(BaseModel):
    email: EmailStr
    nickname: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    birthDate: Optional[datetime] = None
    avatarUrl: Optional[str] = None
    coverImageUrl: Optional[str] = None
    role: str
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    elo: int = 1200

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID4
    player_profile: Optional[PlayerProfile] = None
    referee_profile: Optional[RefereeProfile] = None
    coach_profile: Optional[CoachProfile] = None

    class Config:
        from_attributes = True

# Новые схемы для кнопок профиля
class ProfileButtonAction(BaseModel):
    type: str
    status: Optional[str] = None

class ProfileButton(BaseModel):
    action: ProfileButtonAction
    text: str

# Новая схема ответа для профиля пользователя
class UserProfile(User):
    profile_buttons: List[ProfileButton] = []
