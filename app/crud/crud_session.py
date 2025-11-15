from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Session
from app.schemas.session import SessionCreate, SessionUpdate


class CRUDSession(CRUDBase[Session, SessionCreate, SessionUpdate]):
    async def get_by_refresh_token(self, db: AsyncSession, *, refresh_token: str) -> Session | None:
        statement = select(self.model).where(self.model.refresh_token == refresh_token)
        return (await db.execute(statement)).scalar_one_or_none()


session = CRUDSession(Session)
