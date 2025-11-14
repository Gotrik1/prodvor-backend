
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from pydantic import UUID4

class SubscriptionService:
    async def subscribe(self, db: AsyncSession, *, user_id: UUID4, team_id: UUID4):
        await crud.subscription.subscribe(db=db, user_id=user_id, team_id=team_id)

    async def unsubscribe(self, db: AsyncSession, *, user_id: UUID4, team_id: UUID4):
        await crud.subscription.unsubscribe(db=db, user_id=user_id, team_id=team_id)

    async def is_subscribed(self, db: AsyncSession, *, user_id: UUID4, team_id: UUID4) -> bool:
        return await crud.subscription.is_subscribed(db=db, user_id=user_id, team_id=team_id)

subscription_service = SubscriptionService()
