from pydantic import BaseModel
import uuid

class LikeBase(BaseModel):
    user_id: uuid.UUID
    post_id: int

class LikeCreate(LikeBase):
    pass

class LikeUpdate(LikeBase):
    pass

class LikeInDBBase(LikeBase):
    id: int

    class Config:
        from_attributes = True

class Like(LikeInDBBase):
    pass
