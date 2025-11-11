from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app import dependencies as deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Team])
def read_teams(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve teams.
    """
    teams = crud.team.get_multi(db, skip=skip, limit=limit)
    return teams


@router.post("/", response_model=schemas.Team)
def create_team(
    *,
    db: Session = Depends(deps.get_db),
    team_in: schemas.TeamCreate,
) -> Any:
    """
    Create new team.
    """
    team = crud.team.create(db, obj_in=team_in)
    return team


@router.put("/{team_id}", response_model=schemas.Team)
def update_team(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
    team_in: schemas.TeamUpdate,
) -> Any:
    """
    Update a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=404,
            detail="The team with this id does not exist in the system",
        )
    team = crud.team.update(db, db_obj=team, obj_in=team_in)
    return team


@router.get("/{team_id}", response_model=schemas.Team)
def read_team_by_id(
    team_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific team by id.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=404, detail="The team with this id does not exist in the system"
        )
    return team


@router.delete("/{team_id}", response_model=schemas.Team)
def delete_team(
    *,
    db: Session = Depends(deps.get_db),
    team_id: int,
) -> Any:
    """
    Delete a team.
    """
    team = crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(
            status_code=404,
            detail="The team with this id does not exist in the system",
        )
    team = crud.team.remove(db, id=team_id)
    return team
