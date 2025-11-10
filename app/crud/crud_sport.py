from app.crud.base import CRUDBase
from app.models import Sport
from app.schemas.sport import SportCreate, SportUpdate


class CRUDSport(CRUDBase[Sport, SportCreate, SportUpdate]):
    pass


sport = CRUDSport(Sport)
