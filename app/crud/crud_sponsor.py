from app.crud.base import CRUDBase
from app.models import Sponsor
from app.schemas.sponsor import SponsorCreate, SponsorUpdate


class CRUDSponsor(CRUDBase[Sponsor, SponsorCreate, SponsorUpdate]):
    pass


sponsor = CRUDSponsor(Sponsor)
