
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from fastapi import HTTPException

class SportService:
    async def get_sports(self, db: AsyncSession, *, skip: int, limit: int) -> list[models.Sport]:
        return await crud.sport.get_multi(db, skip=skip, limit=limit)

    async def create_sport(self, db: AsyncSession, *, sport_in: schemas.SportCreate) -> models.Sport:
        sport = await crud.sport.get_by_name(db, name=sport_in.name)
        if sport:
            raise HTTPException(
                status_code=400,
                detail="Sport with this name already exists in the system.",
            )
        return await crud.sport.create(db, obj_in=sport_in)

sport_service = SportService()
