from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models import Sport
from app.schemas.sport import SportCreate, SportUpdate


class CRUDSport(CRUDBase[Sport, SportCreate, SportUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Sport]:
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()


sport = CRUDSport(Sport)
