from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import datetime

# Helper to format datetime objects
def convert_datetime_to_iso_8601(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostInDBBase(PostBase):
    id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: convert_datetime_to_iso_8601
        }
    )

class Post(PostInDBBase):
    pass
