
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.dependencies import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Sport])
def read_sports(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve sports.
    """
    sports = crud.sport.get_multi(db, skip=skip, limit=limit)
    return sports


@router.post("/", response_model=schemas.Sport)
def create_sport(
    *, 
    db: Session = Depends(get_db),
    sport_in: schemas.SportCreate,
):
    """
    Create new sport.
    """
    # Check if sport with this name already exists
    existing_sport = db.query(crud.sport.model).filter(crud.sport.model.name == sport_in.name).first()
    if existing_sport:
        # In a real app, you'd return a 400 error
        # For now, let's just return the existing one
        return existing_sport
        
    sport = crud.sport.create(db=db, obj_in=sport_in)
    return sport
