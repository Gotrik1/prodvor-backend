
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models

class SponsorService:
    async def get_sponsors(self, db: AsyncSession, *, skip: int, limit: int) -> list[models.Sponsor]:
        return await crud.sponsor.get_multi(db, skip=skip, limit=limit)

sponsor_service = SponsorService()
