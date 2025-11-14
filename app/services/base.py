from typing import Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseService:
    async def get_one(self, db: AsyncSession, q: select) -> Optional[ModelType]:
        result = await db.execute(q)
        return result.scalars().first()
