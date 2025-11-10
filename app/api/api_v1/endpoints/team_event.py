from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.TeamEvent])
def read_team_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve team_events.
    """
    team_events = crud.team_event.get_multi(db, skip=skip, limit=limit)
    return team_events


@router.post("/", response_model=schemas.TeamEvent)
def create_team_event(
    *,
    db: Session = Depends(deps.get_db),
    team_event_in: schemas.TeamEventCreate,
) -> Any:
    """
    Create new team_event.
    """
    team_event = crud.team_event.create(db, obj_in=team_event_in)
    return team_event


@router.put("/{team_event_id}", response_model=schemas.TeamEvent)
def update_team_event(
    *,
    db: Session = Depends(deps.get_db),
    team_event_id: int,
    team_event_in: schemas.TeamEventUpdate,
) -> Any:
    """
    Update a team_event.
    """
    team_event = crud.team_event.get(db, id=team_event_id)
    if not team_event:
        raise HTTPException(
            status_code=404,
            detail="The team_event with this id does not exist in the system",
        )
    team_event = crud.team_event.update(db, db_obj=team_event, obj_in=team_event_in)
    return team_event


@router.get("/{team_event_id}", response_model=schemas.TeamEvent)
def read_team_event_by_id(
    team_event_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific team_event by id.
    """
    team_event = crud.team_event.get(db, id=team_event_id)
    if not team_event:
        raise HTTPException(
            status_code=404, detail="The team_event with this id does not exist in the system"
        )
    return team_event


@router.delete("/{team_event_id}", response_model=schemas.TeamEvent)
def delete_team_event(
    *,
    db: Session = Depends(deps.get_db),
    team_event_id: int,
) -> Any:
    """
    Delete a team_event.
    """
    team_event = crud.team_event.get(db, id=team_event_id)
    if not team_event:
        raise HTTPException(
            status_code=404,
            detail="The team_event with this id does not exist in the system",
        )
    team_event = crud.team_event.remove(db, id=team_event_id)
    return team_event
