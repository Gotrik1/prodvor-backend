
from sqlalchemy.orm import Session
import uuid
from .base import CRUDBase
from app.models.sport import Sport
from app.schemas.sport import SportCreate

class CRUDSport(CRUDBase[Sport, SportCreate, SportCreate]):
    def create(self, db: Session, *, obj_in: SportCreate) -> Sport:
        db_obj = Sport(
            id=str(uuid.uuid4()),
            name=obj_in.name,
            isTeamSport=obj_in.isTeamSport
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

sport = CRUDSport(Sport)
