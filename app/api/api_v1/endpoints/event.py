from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app import dependencies as deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Event])
def read_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve events.
    """
    events = crud.event.get_multi(db, skip=skip, limit=limit)
    return events


@router.post("/", response_model=schemas.Event)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: schemas.EventCreate,
) -> Any:
    """
    Create new event.
    """
    event = crud.event.create(db, obj_in=event_in)
    return event


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    event_in: schemas.EventUpdate,
) -> Any:
    """
    Update a event.
    """
    event = crud.event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="The event with this id does not exist in the system",
        )
    event = crud.event.update(db, db_obj=event, obj_in=event_in)
    return event


@router.get("/{event_id}", response_model=schemas.Event)
def read_event_by_id(
    event_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific event by id.
    """
    event = crud.event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=404, detail="The event with this id does not exist in the system"
        )
    return event


@router.delete("/{event_id}", response_model=schemas.Event)
def delete_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
) -> Any:
    """
    Delete a event.
    """
    event = crud.event.get(db, id=event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail="The event with this id does not exist in the system",
        )
    event = crud.event.remove(db, id=event_id)
    return event
