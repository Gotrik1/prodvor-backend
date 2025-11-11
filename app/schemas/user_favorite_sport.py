
from pydantic import BaseModel
import uuid

class UserFavoriteSportBase(BaseModel):
    user_id: uuid.UUID
    sport_id: int

class UserFavoriteSportCreate(UserFavoriteSportBase):
    pass

class UserFavoriteSportUpdate(UserFavoriteSportBase):
    pass

class UserFavoriteSportInDBBase(UserFavoriteSportBase):
    class Config:
        from_attributes = True

class UserFavoriteSport(UserFavoriteSportInDBBase):
    pass
