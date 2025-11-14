
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas

class LFGService:
    async def get_lfgs(
        self, db: AsyncSession, skip: int, limit: int, type: str, sport_id: int, role: str
    ) -> list[models.LFG]:
        return await crud.lfg.get_multi(
            db, skip=skip, limit=limit, type=type, sport_id=sport_id, role=role
        )

    async def create_lfg(
        self,
        db: AsyncSession,
        *, 
        lfg_in: schemas.lfg.LFGCreate,
        creator_id: models.User.id
    ) -> models.LFG:
        if lfg_in.type == "team":
            if not lfg_in.team_id:
                raise HTTPException(
                    status_code=400,
                    detail="team_id is required for type 'team'",
                )
            team = await crud.team.get(db, id=lfg_in.team_id)
            if not team:
                raise HTTPException(
                    status_code=404,
                    detail="Team not found",
                )
            if team.captain_id != creator_id:
                raise HTTPException(
                    status_code=403,
                    detail="Only the team captain can create a 'team' LFG post",
                )
        
        lfg = await crud.lfg.create_with_creator(db, obj_in=lfg_in, creator_id=creator_id)
        return lfg

lfg_service = LFGService()
