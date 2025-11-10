from app.crud.base import CRUDBase
from app.models import UserTeam
from app.schemas.user_team import UserTeamCreate, UserTeamUpdate


class CRUDUserTeam(CRUDBase[UserTeam, UserTeamCreate, UserTeamUpdate]):
    pass


user_team = CRUDUserTeam(UserTeam)
