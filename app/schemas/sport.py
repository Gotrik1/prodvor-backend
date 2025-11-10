from pydantic import BaseModel
from typing import Optional

# Shared properties
class SportBase(BaseModel):
    name: Optional[str] = None

# Properties to receive on item creation
class SportCreate(SportBase):
    name: str

# Properties to receive on item update
class SportUpdate(SportBase):
    pass

# Properties shared by models in DB
class SportInDBBase(SportBase):
    id: int
    name: str

    class Config:
        orm_mode = True

# Properties to return to client
class Sport(SportInDBBase):
    pass

# Properties stored in DB
class SportInDB(SportInDBBase):
    pass
