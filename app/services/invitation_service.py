
import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.schemas.invitation import InvitationCreate, InvitationUpdate
from app.models.invitation import InvitationStatus

class InvitationService:
    async def create_invitation(
        self, db: AsyncSession, *, invitation_in: InvitationCreate
    ) -> models.Invitation:
        # Business logic for creation can be added here
        return await crud.invitation.create(db=db, obj_in=invitation_in)

    async def get_user_invitations(
        self, db: AsyncSession, *, user_id: uuid.UUID
    ) -> List[models.Invitation]:
        return await crud.invitation.get_user_invitations(db=db, user_id=user_id)

    async def get_invitation(
        self, db: AsyncSession, *, invitation_id: uuid.UUID
    ) -> models.Invitation:
        invitation = await crud.invitation.get(db=db, id=invitation_id)
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        return invitation

    async def accept_invitation(
        self, db: AsyncSession, *, invitation_id: uuid.UUID
    ) -> models.Invitation:
        invitation = await self.get_invitation(db=db, invitation_id=invitation_id)
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=400, detail="Invitation is not pending")
        
        update_data = InvitationUpdate(status=InvitationStatus.ACCEPTED)
        return await crud.invitation.update(db=db, db_obj=invitation, obj_in=update_data)

    async def decline_invitation(
        self, db: AsyncSession, *, invitation_id: uuid.UUID
    ) -> models.Invitation:
        invitation = await self.get_invitation(db=db, invitation_id=invitation_id)
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=400, detail="Invitation is not pending")

        update_data = InvitationUpdate(status=InvitationStatus.DECLINED)
        return await crud.invitation.update(db=db, db_obj=invitation, obj_in=update_data)

invitation_service = InvitationService()
