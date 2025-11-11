from pydantic import BaseModel
import uuid

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

    class Config:
        from_attributes = True

class Comment(CommentInDBBase):
    pass
