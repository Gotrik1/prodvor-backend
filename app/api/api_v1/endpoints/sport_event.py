from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app import dependencies as deps

router = APIRouter()


@router.get("/", response_model=List[schemas.SportEvent])
def read_sport_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sport_events.
    """
    sport_events = crud.sport_event.get_multi(db, skip=skip, limit=limit)
    return sport_events


@router.post("/", response_model=schemas.SportEvent)
def create_sport_event(
    *,
    db: Session = Depends(deps.get_db),
    sport_event_in: schemas.SportEventCreate,
) -> Any:
    """
    Create new sport_event.
    """
    sport_event = crud.sport_event.create(db, obj_in=sport_event_in)
    return sport_event


@router.put("/{sport_event_id}", response_model=schemas.SportEvent)
def update_sport_event(
    *,
    db: Session = Depends(deps.get_db),
    sport_event_id: int,
    sport_event_in: schemas.SportEventUpdate,
) -> Any:
    """
    Update a sport_event.
    """
    sport_event = crud.sport_event.get(db, id=sport_event_id)
    if not sport_event:
        raise HTTPException(
            status_code=404,
            detail="The sport_event with this id does not exist in the system",
        )
    sport_event = crud.sport_event.update(db, db_obj=sport_event, obj_in=sport_event_in)
    return sport_event


@router.get("/{sport_event_id}", response_model=schemas.SportEvent)
def read_sport_event_by_id(
    sport_event_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific sport_event by id.
    """
    sport_event = crud.sport_event.get(db, id=sport_event_id)
    if not sport_event:
        raise HTTPException(
            status_code=404, detail="The sport_event with this id does not exist in the system"
        )
    return sport_event


@router.delete("/{sport_event_id}", response_model=schemas.SportEvent)
def delete_sport_event(
    *,
    db: Session = Depends(deps.get_db),
    sport_event_id: int,
) -> Any:
    """
    Delete a sport_event.
    """
    sport_event = crud.sport_event.get(db, id=sport_event_id)
    if not sport_event:
        raise HTTPException(
            status_code=404,
            detail="The sport_event with this id does not exist in the system",
        )
    sport_event = crud.sport_event.remove(db, id=sport_event_id)
    return sport_event
