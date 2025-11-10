
from pydantic import BaseModel

# Схема для создания и чтения Sport
class SportBase(BaseModel):
    name: str
    isTeamSport: bool

class SportCreate(SportBase):
    pass

class Sport(SportBase):
    id: str

    class Config:
        from_attributes = True
