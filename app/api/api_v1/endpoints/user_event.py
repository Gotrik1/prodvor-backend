from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app import dependencies as deps

router = APIRouter()


@router.get("/", response_model=List[schemas.UserEvent])
def read_user_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve user_events.
    """
    user_events = crud.user_event.get_multi(db, skip=skip, limit=limit)
    return user_events


@router.post("/", response_model=schemas.UserEvent)
def create_user_event(
    *,
    db: Session = Depends(deps.get_db),
    user_event_in: schemas.UserEventCreate,
) -> Any:
    """
    Create new user_event.
    """
    user_event = crud.user_event.create(db, obj_in=user_event_in)
    return user_event


@router.put("/{user_event_id}", response_model=schemas.UserEvent)
def update_user_event(
    *,
    db: Session = Depends(deps.get_db),
    user_event_id: int,
    user_event_in: schemas.UserEventUpdate,
) -> Any:
    """
    Update a user_event.
    """
    user_event = crud.user_event.get(db, id=user_event_id)
    if not user_event:
        raise HTTPException(
            status_code=404,
            detail="The user_event with this id does not exist in the system",
        )
    user_event = crud.user_event.update(db, db_obj=user_event, obj_in=user_event_in)
    return user_event


@router.get("/{user_event_id}", response_model=schemas.UserEvent)
def read_user_event_by_id(
    user_event_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user_event by id.
    """
    user_event = crud.user_event.get(db, id=user_event_id)
    if not user_event:
        raise HTTPException(
            status_code=404, detail="The user_event with this id does not exist in the system"
        )
    return user_event


@router.delete("/{user_event_id}", response_model=schemas.UserEvent)
def delete_user_event(
    *,
    db: Session = Depends(deps.get_db),
    user_event_id: int,
) -> Any:
    """
    Delete a user_event.
    """
    user_event = crud.user_event.get(db, id=user_event_id)
    if not user_event:
        raise HTTPException(
            status_code=404,
            detail="The user_event with this id does not exist in the system",
        )
    user_event = crud.user_event.remove(db, id=user_event_id)
    return user_event
