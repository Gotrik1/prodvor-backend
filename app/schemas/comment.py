from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class CommentBase(BaseModel):
    content: str
    user_id: uuid.UUID
    post_id: int

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class CommentInDBBase(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Comment(CommentInDBBase):
    pass
