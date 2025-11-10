from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    author_id: uuid.UUID

class PostUpdate(PostBase):
    pass

class PostInDBBase(PostBase):
    id: int
    author_id: uuid.UUID
    created_at: datetime

    class Config:
        orm_mode = True

class Post(PostInDBBase):
    pass
