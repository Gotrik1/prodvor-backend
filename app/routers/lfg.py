
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.lfg.LFG])
def read_lfgs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: str = None,
    sport_id: int = None,
    role: str = None,
):
    """
    Retrieve LFG posts.
    """
    lfgs = crud.lfg.get_multi(db, skip=skip, limit=limit, type=type, sport_id=sport_id, role=role)
    return lfgs

@router.post("", response_model=schemas.lfg.LFG)
def create_lfg(
    *,
    db: Session = Depends(get_db),
    lfg_in: schemas.lfg.LFGCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new LFG post.
    """
    if lfg_in.type == "team":
        if not lfg_in.team_id:
            raise HTTPException(
                status_code=400,
                detail="team_id is required for type 'team'",
            )
        team = crud.team.get(db, id=lfg_in.team_id)
        if not team:
            raise HTTPException(
                status_code=404,
                detail="Team not found",
            )
        if team.captain_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the team captain can create a 'team' LFG post",
            )

    lfg = crud.lfg.create(db, obj_in=lfg_in, author_id=current_user.id)
    return lfg
