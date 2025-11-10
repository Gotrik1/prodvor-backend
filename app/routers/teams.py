
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.team.Team])
def read_teams(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve teams.
    """
    teams = crud.team.get_multi(db, skip=skip, limit=limit)
    return teams

@router.post("", response_model=schemas.team.Team)
def create_team(
    *,
    db: Session = Depends(get_db),
    team_in: schemas.team.TeamCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new team.
    """
    sport = crud.sport.get(db, id=team_in.sport_id)
    if not sport:
        raise HTTPException(
            status_code=404,
            detail="Sport not found",
        )
    team = crud.team.create_with_captain(db, obj_in=team_in, captain_id=current_user.id)
    return team

@router.get("/{team_id}", response_model=schemas.team.Team)
def read_team(
    *,
    db: Session = Depends(get_db),
    team_id: int,
):
    """
    Get team by ID.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )
    return team

@router.delete("/{team_id}/members/{user_id}", response_model=Any)
def remove_member(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    user_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """
    Remove a member from a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the captain can remove members")
    if team.captain_id == user_id:
        raise HTTPException(status_code=400, detail="Captain cannot remove themselves")
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in team.members:
        raise HTTPException(status_code=404, detail="Player is not a member of this team")
    crud.team.remove_member(db, team=team, user=user)
    return {"message": "Player removed successfully"}

@router.post("/{team_id}/logo", response_model=schemas.team.Team)
def update_team_logo(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    logo_in: schemas.team.TeamUpdate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Update team logo.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the captain can update the logo")
    team = crud.team.update(db, db_obj=team, obj_in=logo_in)
    return team

@router.post("/{team_id}/apply", response_model=Any)
def apply_to_team(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """
    Apply to a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if current_user in team.members:
        raise HTTPException(status_code=400, detail="You are already a member of this team")
    existing_application = crud.team.get_application(db, team_id=team_id, user_id=current_user.id)
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied to this team")
    crud.team.create_application(db, team_id=team_id, user_id=current_user.id)
    return {"message": "Application sent successfully"}

@router.get("/{team_id}/applications", response_model=List[schemas.user.User])
def get_applications(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """
    Get team applications.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the captain can view applications")
    applications = crud.team.get_applications(db, team_id=team_id)
    return applications

@router.post("/{team_id}/applications/{user_id}/respond", response_model=Any)
def respond_to_application(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    user_id: int,
    action: str,
    current_user: models.User = Depends(get_current_user),
):
    """
    Respond to a team application.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the captain can respond to applications")
    application = crud.team.get_application(db, team_id=team_id, user_id=user_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if action == "accept":
        user = crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        crud.team.add_member(db, team=team, user=user)
        crud.team.delete_application(db, application=application)
        return {"message": "Player accepted"}
    elif action == "decline":
        crud.team.delete_application(db, application=application)
        return {"message": "Player declined"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@router.post("/{team_id}/follow", response_model=Any)
def follow_team(
    *,
    db: Session = Depends(get_db),
    team_id: int,
    current_user: models.User = Depends(get_current_user),
):
    """
    Follow/unfollow a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team in current_user.following_teams:
        crud.user.unfollow_team(db, user=current_user, team=team)
        return {"isFollowing": False}
    else:
        crud.user.follow_team(db, user=current_user, team=team)
        return {"isFollowing": True}
