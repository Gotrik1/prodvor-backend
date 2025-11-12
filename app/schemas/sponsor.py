from pydantic import BaseModel, ConfigDict
from typing import Optional

class SponsorBase(BaseModel):
    name: str
    logoUrl: Optional[str] = None
    contribution: Optional[str] = None

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(SponsorBase):
    pass

class SponsorInDBBase(SponsorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Sponsor(SponsorInDBBase):
    pass
