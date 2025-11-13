# app/crud/crud_subscription.py
from __future__ import annotations
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.subscription import Subscription

async def is_subscribed(db: AsyncSession, *, user_id: UUID, team_id: UUID) -> bool:
    q = (
        select(Subscription.id)
        .where(Subscription.user_id == user_id, Subscription.team_id == team_id)
        .limit(1)
    )
    return (await db.execute(q)).first() is not None

async def subscribe(db: AsyncSession, *, user_id: UUID, team_id: UUID) -> None:
    # upsert, чтобы не плодить дубликаты
    stmt = (
        pg_insert(Subscription)
        .values(user_id=user_id, team_id=team_id)
        .on_conflict_do_nothing(index_elements=["user_id", "team_id"])
    )
    await db.execute(stmt)
    await db.commit()


async def unsubscribe(db: AsyncSession, *, user_id: UUID, team_id: UUID) -> int:
    stmt = delete(Subscription).where(
        Subscription.user_id == user_id, Subscription.team_id == team_id
    )
    res = await db.execute(stmt)
    await db.commit()
    return res.rowcount


async def list_followed_team_ids(db: AsyncSession, *, user_id: UUID) -> list[UUID]:
    q = select(Subscription.team_id).where(Subscription.user_id == user_id)
    res = await db.execute(q)
    return [row[0] for row in res.all()]
