from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class CommentBase(BaseModel):
    text: str
    postId: uuid.UUID

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class CommentInDBBase(CommentBase):
    id: uuid.UUID
    authorId: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Comment(CommentInDBBase):
    pass
