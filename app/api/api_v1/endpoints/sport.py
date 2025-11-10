from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Sport])
def read_sports(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sports.
    """
    sports = crud.sport.get_multi(db, skip=skip, limit=limit)
    return sports


@router.post("/", response_model=schemas.Sport)
def create_sport(
    *,
    db: Session = Depends(deps.get_db),
    sport_in: schemas.SportCreate,
) -> Any:
    """
    Create new sport.
    """
    sport = crud.sport.create(db, obj_in=sport_in)
    return sport


@router.put("/{sport_id}", response_model=schemas.Sport)
def update_sport(
    *,
    db: Session = Depends(deps.get_db),
    sport_id: int,
    sport_in: schemas.SportUpdate,
) -> Any:
    """
    Update a sport.
    """
    sport = crud.sport.get(db, id=sport_id)
    if not sport:
        raise HTTPException(
            status_code=404,
            detail="The sport with this id does not exist in the system",
        )
    sport = crud.sport.update(db, db_obj=sport, obj_in=sport_in)
    return sport


@router.get("/{sport_id}", response_model=schemas.Sport)
def read_sport_by_id(
    sport_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific sport by id.
    """
    sport = crud.sport.get(db, id=sport_id)
    if not sport:
        raise HTTPException(
            status_code=404, detail="The sport with this id does not exist in the system"
        )
    return sport


@router.delete("/{sport_id}", response_model=schemas.Sport)
def delete_sport(
    *,
    db: Session = Depends(deps.get_db),
    sport_id: int,
) -> Any:
    """
    Delete a sport.
    """
    sport = crud.sport.get(db, id=sport_id)
    if not sport:
        raise HTTPException(
            status_code=404,
            detail="The sport with this id does not exist in the system",
        )
    sport = crud.sport.remove(db, id=sport_id)
    return sport
