from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("", response_model=schemas.Invitation, dependencies=[Depends(get_current_user)])
def create_invitation(
    *, 
    db: Session = Depends(get_db),
    invitation_in: schemas.InvitationCreate,
    current_user: models.User = Depends(get_current_user) # Assuming the inviter is the current user
):
    # Add logic here to ensure only team admins can invite
    return crud.invitation.create_invitation(db=db, obj_in=invitation_in)

@router.get("/user/{user_id}", response_model=list[schemas.Invitation], dependencies=[Depends(get_current_user)])
def get_user_invitations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Authorization: ensure the current user can view these invitations
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these invitations")
    return crud.invitation.get_invitations_for_user(db=db, user_id=user_id)

@router.put("/{invitation_id}/accept", response_model=schemas.Invitation, dependencies=[Depends(get_current_user)])
def accept_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invitation = crud.invitation.accept_invitation(db=db, invitation_id=invitation_id, user_id=current_user.id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or you are not the invited user")
    return invitation

@router.put("/{invitation_id}/decline", response_model=schemas.Invitation, dependencies=[Depends(get_current_user)])
def decline_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    invitation = crud.invitation.decline_invitation(db=db, invitation_id=invitation_id, user_id=current_user.id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or you are not the invited user")
    return invitation
