from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.UserFavoriteSport])
def read_user_favorite_sports(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve user_favorite_sports.
    """
    user_favorite_sports = crud.user_favorite_sport.get_multi(db, skip=skip, limit=limit)
    return user_favorite_sports


@router.post("/", response_model=schemas.UserFavoriteSport)
def create_user_favorite_sport(
    *,
    db: Session = Depends(deps.get_db),
    user_favorite_sport_in: schemas.UserFavoriteSportCreate,
) -> Any:
    """
    Create new user_favorite_sport.
    """
    user_favorite_sport = crud.user_favorite_sport.create(db, obj_in=user_favorite_sport_in)
    return user_favorite_sport


@router.put("/{user_favorite_sport_id}", response_model=schemas.UserFavoriteSport)
def update_user_favorite_sport(
    *,
    db: Session = Depends(deps.get_db),
    user_favorite_sport_id: int,
    user_favorite_sport_in: schemas.UserFavoriteSportUpdate,
) -> Any:
    """
    Update a user_favorite_sport.
    """
    user_favorite_sport = crud.user_favorite_sport.get(db, id=user_favorite_sport_id)
    if not user_favorite_sport:
        raise HTTPException(
            status_code=404,
            detail="The user_favorite_sport with this id does not exist in the system",
        )
    user_favorite_sport = crud.user_favorite_sport.update(db, db_obj=user_favorite_sport, obj_in=user_favorite_sport_in)
    return user_favorite_sport


@router.get("/{user_favorite_sport_id}", response_model=schemas.UserFavoriteSport)
def read_user_favorite_sport_by_id(
    user_favorite_sport_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user_favorite_sport by id.
    """
    user_favorite_sport = crud.user_favorite_sport.get(db, id=user_favorite_sport_id)
    if not user_favorite_sport:
        raise HTTPException(
            status_code=404, detail="The user_favorite_sport with this id does not exist in the system"
        )
    return user_favorite_sport


@router.delete("/{user_favorite_sport_id}", response_model=schemas.UserFavoriteSport)
def delete_user_favorite_sport(
    *,
    db: Session = Depends(deps.get_db),
    user_favorite_sport_id: int,
) -> Any:
    """
    Delete a user_favorite_sport.
    """
    user_favorite_sport = crud.user_favorite_sport.get(db, id=user_favorite_sport_id)
    if not user_favorite_sport:
        raise HTTPException(
            status_code=404,
            detail="The user_favorite_sport with this id does not exist in the system",
        )
    user_favorite_sport = crud.user_favorite_sport.remove(db, id=user_favorite_sport_id)
    return user_favorite_sport
