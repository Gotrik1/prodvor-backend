from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.lfg import LFG
from app.schemas.lfg import LFGCreate, LFGUpdate


class CRUDLFG(CRUDBase[LFG, LFGCreate, LFGUpdate]):
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, type: Optional[str] = None, sport_id: Optional[int] = None, role: Optional[str] = None
    ) -> List[LFG]:
        query = select(self.model)
        if type:
            query = query.where(self.model.type == type)
        if sport_id:
            query = query.where(self.model.sport_id == sport_id)
        if role:
            query = query.where(self.model.role == role)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, *, obj_in: LFGCreate, creator_id: int) -> LFG:
        obj_in_data = obj_in.dict()
        obj_in_data['creator_id'] = creator_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


lfg = CRUDLFG(LFG)
