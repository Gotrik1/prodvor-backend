from app.crud.base import CRUDBase
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate, InvitationUpdate

class CRUDInvitation(CRUDBase[Invitation, InvitationCreate, InvitationUpdate]):
    pass

invitation = CRUDInvitation(Invitation)
