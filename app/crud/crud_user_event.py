from app.crud.base import CRUDBase
from app.models import UserEvent
from app.schemas.user_event import UserEventCreate, UserEventUpdate


class CRUDUserEvent(CRUDBase[UserEvent, UserEventCreate, UserEventUpdate]):
    pass


user_event = CRUDUserEvent(UserEvent)
