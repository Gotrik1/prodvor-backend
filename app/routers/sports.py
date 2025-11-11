
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.sport.Sport])
async def read_sports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve sports.
    """
    sports = await crud.sport.get_multi(db, skip=skip, limit=limit)
    return sports

@router.post("", response_model=schemas.sport.Sport)
async def create_sport(
    *,
    db: Session = Depends(get_db),
    sport_in: schemas.sport.SportCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new sport.
    """
    sport = await crud.sport.get_by_name(db, name=sport_in.name)
    if sport:
        raise HTTPException(
            status_code=400,
            detail="Sport with this name already exists in the system.",
        )
    sport = await crud.sport.create(db, obj_in=sport_in)
    return sport
