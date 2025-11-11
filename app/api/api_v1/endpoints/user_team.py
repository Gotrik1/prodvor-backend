from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app import dependencies as deps

router = APIRouter()


@router.get("/", response_model=List[schemas.UserTeam])
def read_user_teams(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve user_teams.
    """
    user_teams = crud.user_team.get_multi(db, skip=skip, limit=limit)
    return user_teams


@router.post("/", response_model=schemas.UserTeam)
def create_user_team(
    *,
    db: Session = Depends(deps.get_db),
    user_team_in: schemas.UserTeamCreate,
) -> Any:
    """
    Create new user_team.
    """
    user_team = crud.user_team.create(db, obj_in=user_team_in)
    return user_team


@router.put("/{user_team_id}", response_model=schemas.UserTeam)
def update_user_team(
    *,
    db: Session = Depends(deps.get_db),
    user_team_id: int,
    user_team_in: schemas.UserTeamUpdate,
) -> Any:
    """
    Update a user_team.
    """
    user_team = crud.user_team.get(db, id=user_team_id)
    if not user_team:
        raise HTTPException(
            status_code=404,
            detail="The user_team with this id does not exist in the system",
        )
    user_team = crud.user_team.update(db, db_obj=user_team, obj_in=user_team_in)
    return user_team


@router.get("/{user_team_id}", response_model=schemas.UserTeam)
def read_user_team_by_id(
    user_team_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user_team by id.
    """
    user_team = crud.user_team.get(db, id=user_team_id)
    if not user_team:
        raise HTTPException(
            status_code=404, detail="The user_team with this id does not exist in the system"
        )
    return user_team


@router.delete("/{user_team_id}", response_model=schemas.UserTeam)
def delete_user_team(
    *,
    db: Session = Depends(deps.get_db),
    user_team_id: int,
) -> Any:
    """
    Delete a user_team.
    """
    user_team = crud.user_team.get(db, id=user_team_id)
    if not user_team:
        raise HTTPException(
            status_code=404,
            detail="The user_team with this id does not exist in the system",
        )
    user_team = crud.user_team.remove(db, id=user_team_id)
    return user_team
