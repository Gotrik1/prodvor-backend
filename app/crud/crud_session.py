from app.crud.base import CRUDBase
from app.models import Session
from app.schemas.session import SessionCreate, SessionUpdate


class CRUDSession(CRUDBase[Session, SessionCreate, SessionUpdate]):
    pass


session = CRUDSession(Session)
