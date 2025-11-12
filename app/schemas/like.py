from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class LikeBase(BaseModel):
    user_id: uuid.UUID
    post_id: uuid.UUID

class LikeCreateRequest(BaseModel):
    post_id: uuid.UUID

class LikeCreate(LikeBase):
    pass

class LikeUpdate(LikeBase):
    pass

class LikeCount(BaseModel):
    count: int

class LikeInDBBase(LikeBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Like(LikeInDBBase):
    pass
