from app.crud.base import CRUDBase
from app.models import SportEvent
from app.schemas.sport_event import SportEventCreate, SportEventUpdate


class CRUDSportEvent(CRUDBase[SportEvent, SportEventCreate, SportEventUpdate]):
    pass


sport_event = CRUDSportEvent(SportEvent)
