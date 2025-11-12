from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
from app.schemas.auth import Msg

router = APIRouter()

class LogoUpdate(BaseModel):
    logoUrl: str | None = None

@router.get("", response_model=List[schemas.team.Team])
async def read_teams(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve teams.
    """
    teams = await crud.team.get_multi(db, skip=skip, limit=limit)
    return teams

@router.post("", response_model=schemas.team.Team, dependencies=[Depends(get_current_user)])
async def create_team(
    *,
    db: AsyncSession = Depends(get_db),
    team_in: schemas.team.TeamCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new team.
    """
    sport = await crud.sport.get(db, id=team_in.sport_id)
    if not sport:
        raise HTTPException(
            status_code=404,
            detail="Sport not found",
        )
    team = await crud.team.create_with_captain(db, obj_in=team_in, captain_id=current_user.id)
    return team

@router.get("/{team_id}", response_model=schemas.team.Team)
async def get_team(team_id: UUID,
                   db: AsyncSession = Depends(get_db)):
    team = await crud.team.get(db, id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/{team_id}/apply")
async def apply(team_id: UUID,
                db: AsyncSession = Depends(get_db),
                current_user = Depends(get_current_user)):
    await crud.team.apply(db, team_id=team_id, user_id=current_user.id)
    return {"message": "Application sent successfully"}

@router.get("/{team_id}/applications")
async def list_applications(team_id: UUID,
                            db: AsyncSession = Depends(get_db),
                            current_user = Depends(get_current_user)):
    # капитан видит заявки
    return await crud.team.list_applications(db, team_id=team_id, captain_id=current_user.id)

@router.post("/{team_id}/applications/{user_id}/respond")
async def respond(team_id: UUID, user_id: UUID,
                  action: str = Query(..., pattern="^(accept|decline)$"),
                  db: AsyncSession = Depends(get_db),
                  current_user = Depends(get_current_user)):
    if action == "accept":
        await crud.team.accept(db, team_id=team_id, captain_id=current_user.id, user_id=user_id)
        return {"message": "Player accepted"}
    else:
        await crud.team.decline(db, team_id=team_id, captain_id=current_user.id, user_id=user_id)
        return {"message": "Player declined"}

@router.post("/{team_id}/logo", response_model=schemas.team.Team)
async def update_logo(team_id: UUID, payload: LogoUpdate,
                      db: AsyncSession = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    team = await crud.team.update_logo(db, team_id=team_id, captain_id=current_user.id, logo_url=payload.logoUrl)
    return team

@router.post("/{team_id}/follow")
async def toggle_follow(team_id: UUID,
                        db: AsyncSession = Depends(get_db),
                        current_user = Depends(get_current_user)):
    is_following = await crud.subscription.toggle_follow_team(
        db, subscriber_id=current_user.id, team_id=team_id
    )
    return {"isFollowing": bool(is_following)}

@router.delete("/{team_id}/members/{user_id}", response_model=Msg)
async def remove_member(team_id: UUID, user_id: UUID,
                        db: AsyncSession = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    await crud.team.remove_member(db, team_id=team_id, captain_id=current_user.id, user_id=user_id)
    return {"message": "Player removed successfully"}
