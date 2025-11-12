# app/crud/crud_notification.py
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification
import uuid

async def get_notifications_for_user(db: AsyncSession, user_id: uuid.UUID):
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(desc(Notification.created_at))
    )
    res = await db.execute(stmt)
    return [row[0] for row in res.all()]
