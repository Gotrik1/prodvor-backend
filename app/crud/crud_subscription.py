# app/crud/crud_subscription.py

from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import team_followers
from app.models.subscription import Subscription


async def is_subscribed(db: AsyncSession, user_id: UUID, team_id: UUID) -> bool:
    result = await db.execute(
        select(team_followers).where(
            team_followers.c.user_id == user_id,
            team_followers.c.team_id == team_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def subscribe(db: AsyncSession, user_id: UUID, team_id: UUID) -> None:
    stmt = (
        pg_insert(team_followers)
        .values(user_id=user_id, team_id=team_id)
        .on_conflict_do_nothing(index_elements=["user_id", "team_id"])
    )
    await db.execute(stmt)
    await db.commit()


async def unsubscribe(db: AsyncSession, user_id: UUID, team_id: UUID) -> int:
    result = await db.execute(
        delete(team_followers).where(
            team_followers.c.user_id == user_id,
            team_followers.c.team_id == team_id,
        )
    )
    await db.commit()
    return result.rowcount


async def toggle(db: AsyncSession, user_id: UUID, team_id: UUID) -> bool:
    """
    Тогглит подписку и возвращает новое состояние:
    True  – пользователь теперь подписан
    False – пользователь теперь отписан
    """
    deleted_count = await unsubscribe(db, user_id, team_id)

    if deleted_count > 0:
        return False  # Успешно отписались
    else:
        await subscribe(db, user_id, team_id)
        return True  # Подписки не было, поэтому подписались
