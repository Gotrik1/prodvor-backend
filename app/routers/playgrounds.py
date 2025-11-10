
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.playground.Playground])
def read_playgrounds(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve playgrounds.
    """
    playgrounds = crud.playground.get_multi(db, skip=skip, limit=limit)
    return playgrounds

@router.post("", response_model=schemas.playground.Playground)
def create_playground(
    *,
    db: Session = Depends(get_db),
    playground_in: schemas.playground.PlaygroundCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new playground.
    """
    playground = crud.playground.create(db, obj_in=playground_in)
    return playground
