# app/crud/crud_subscription.py
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.subscription import Subscription
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

async def subscribe(db: AsyncSession, *, user_id: UUID, team_id: UUID):
    ins = (
        pg_insert(Subscription)
        .values(user_id=user_id, team_id=team_id)
        .on_conflict_do_nothing(index_elements=["user_id", "team_id"])
    )
    await db.execute(ins)
    await db.commit()

async def unsubscribe(db: AsyncSession, *, user_id: UUID, team_id: UUID):
    del_stmt = delete(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.team_id == team_id,
    )
    await db.execute(del_stmt)
    await db.commit()

async def get_subscription_status(db: AsyncSession, *, user_id: UUID, team_id: UUID) -> bool:
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.team_id == team_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None

async def toggle_subscription(db: AsyncSession, *, user_id: UUID, team_id: UUID) -> bool:
    stmt = select(Subscription).where(
        Subscription.user_id == user_id,
        Subscription.team_id == team_id,
    )
    result = await db.execute(stmt)
    existing_subscription = result.scalar_one_or_none()

    if existing_subscription:
        # Subscription exists, so we are unfollowing.
        await db.delete(existing_subscription)
        await db.commit()
        return False
    else:
        # Subscription does not exist, so we are following.
        new_subscription = Subscription(user_id=user_id, team_id=team_id)
        db.add(new_subscription)
        await db.commit()
        return True
