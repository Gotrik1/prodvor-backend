from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate

class CRUDInvitation:
    async def create_invitation(self, db: AsyncSession, obj_in: InvitationCreate) -> Invitation:
        inv = Invitation(user_id=obj_in.user_id, team_id=obj_in.team_id, status='pending')
        db.add(inv)
        await db.flush()           
        await db.commit()
        await db.refresh(inv)      
        return inv

    async def get_user_invitations(self, db: AsyncSession, user_id: UUID) -> List[Invitation]:
        stmt = select(Invitation).where(Invitation.user_id == user_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def accept(self, db: AsyncSession, invitation_id: UUID) -> Optional[Invitation]:
        inv = await db.get(Invitation, invitation_id)
        if not inv:
            return None
        inv.status = 'accepted'
        await db.commit()
        await db.refresh(inv)
        return inv

    async def decline(self, db: AsyncSession, invitation_id: UUID) -> Optional[Invitation]:
        inv = await db.get(Invitation, invitation_id)
        if not inv:
            return None
        inv.status = 'declined'
        await db.commit()
        await db.refresh(inv)
        return inv

invitation = CRUDInvitation()