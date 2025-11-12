from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.sponsor.Sponsor])
async def read_sponsors(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve sponsors.
    """
    sponsors = await crud.sponsor.get_multi(db, skip=skip, limit=limit)
    return sponsors
