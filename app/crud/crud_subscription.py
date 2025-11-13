# app/crud/crud_subscription.py

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription


async def is_subscribed(db: AsyncSession, user_id: UUID, team_id: UUID) -> bool:
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.team_id == team_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def subscribe(db: AsyncSession, user_id: UUID, team_id: UUID) -> None:
    db.add(Subscription(user_id=user_id, team_id=team_id))
    await db.commit()


async def unsubscribe(db: AsyncSession, user_id: UUID, team_id: UUID) -> None:
    await db.execute(
        delete(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.team_id == team_id,
        )
    )
    await db.commit()


async def toggle(db: AsyncSession, user_id: UUID, team_id: UUID) -> bool:
    """
    Тогглит подписку и возвращает новое состояние:
    True  – пользователь теперь подписан
    False – пользователь теперь отписан
    """
    currently_subscribed = await is_subscribed(db, user_id, team_id)

    if currently_subscribed:
        await unsubscribe(db, user_id, team_id)
        return False
    else:
        await subscribe(db, user_id, team_id)
        return True
