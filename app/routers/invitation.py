from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.dependencies import get_db, get_current_user
from app import crud
from app.schemas.invitation import Invitation as InvitationSchema, InvitationCreate

router = APIRouter()

@router.post("", response_model=InvitationSchema)
async def create_invitation(invitation_in: InvitationCreate,
                            db: AsyncSession = Depends(get_db),
                            user=Depends(get_current_user)):
    inv = await crud.invitation.create_invitation(db=db, obj_in=invitation_in)
    return inv

@router.get("/user/{user_id}", response_model=list[InvitationSchema])
async def get_user_invitations(user_id: UUID,
                               db: AsyncSession = Depends(get_db),
                               user=Depends(get_current_user)):
    return await crud.invitation.get_user_invitations(db=db, user_id=user_id)

@router.put("/{invitation_id}/accept", response_model=InvitationSchema)
async def accept_invitation(invitation_id: UUID,
                            db: AsyncSession = Depends(get_db),
                            user=Depends(get_current_user)):
    inv = await crud.invitation.accept(db, invitation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return inv

@router.put("/{invitation_id}/decline", response_model=InvitationSchema)
async def decline_invitation(invitation_id: UUID,
                             db: AsyncSession = Depends(get_db),
                             user=Depends(get_current_user)):
    inv = await crud.invitation.decline(db, invitation_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return inv
