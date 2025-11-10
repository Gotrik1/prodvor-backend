from pydantic import BaseModel
from typing import Optional

class PlaygroundBase(BaseModel):
    name: str
    location: str
    sports: Optional[str] = None # Or a list of sports

class PlaygroundCreate(PlaygroundBase):
    pass

class PlaygroundUpdate(PlaygroundBase):
    pass

class PlaygroundInDBBase(PlaygroundBase):
    id: int

    class Config:
        orm_mode = True

class Playground(PlaygroundInDBBase):
    pass
