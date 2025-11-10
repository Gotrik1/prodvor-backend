from app.crud.base import CRUDBase
from app.models import Team
from app.schemas.team import TeamCreate, TeamUpdate


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    pass


team = CRUDTeam(Team)
