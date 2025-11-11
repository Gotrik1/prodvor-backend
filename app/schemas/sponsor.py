from pydantic import BaseModel
from typing import Optional

class SponsorBase(BaseModel):
    name: str
    logo: Optional[str] = None
    website: Optional[str] = None

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(SponsorBase):
    pass

class SponsorInDBBase(SponsorBase):
    id: int

    class Config:
        from_attributes = True

class Sponsor(SponsorInDBBase):
    pass
