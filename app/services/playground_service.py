
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas

class PlaygroundService:
    async def get_playgrounds(self, db: AsyncSession, *, skip: int, limit: int) -> list[models.playground]:
        return await crud.playground.get_multi(db, skip=skip, limit=limit)

    async def create_playground(self, db: AsyncSession, *, playground_in: schemas.PlaygroundCreate) -> models.playground:
        return await crud.playground.create(db, obj_in=playground_in)

playground_service = PlaygroundService()
