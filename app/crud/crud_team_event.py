from app.crud.base import CRUDBase
from app.models import TeamEvent
from app.schemas.team_event import TeamEventCreate, TeamEventUpdate


class CRUDTeamEvent(CRUDBase[TeamEvent, TeamEventCreate, TeamEventUpdate]):
    pass


team_event = CRUDTeamEvent(TeamEvent)
