from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class LikeBase(BaseModel):
    user_id: uuid.UUID
    post_id: int

class LikeCreate(LikeBase):
    pass

class LikeUpdate(LikeBase):
    pass

class LikeInDBBase(LikeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Like(LikeInDBBase):
    pass
