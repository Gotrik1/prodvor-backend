
# app/crud/crud_subscription.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Subscription, Notification
import uuid

async def follow_team(db: AsyncSession, subscriber_id: uuid.UUID, team_id: uuid.UUID) -> bool:
    # Check if subscription already exists
    stmt = select(Subscription).where(
        Subscription.subscriber_id == subscriber_id,
        Subscription.team_id == team_id
    )
    existing_subscription = await db.execute(stmt)
    if existing_subscription.scalars().first():
        return False  # Already following

    # Create new subscription
    new_subscription = Subscription(subscriber_id=subscriber_id, team_id=team_id)
    db.add(new_subscription)

    # Create a notification for the team captain
    # (Assuming we can get the team captain's ID from the team_id)
    # This part might need adjustment based on how to get the captain's ID.
    # For now, let's assume a function get_team_captain exists or is added.
    # from .crud_team import team as crud_team
    # team = await crud_team.get(db, id=team_id)
    # if team:
    #     notification = Notification(
    #         user_id=team.captain_id,
    #         message=f"A new user has subscribed to your team."
    #     )
    #     db.add(notification)
    
    await db.commit()
    return True

async def unfollow_team(db: AsyncSession, subscriber_id: uuid.UUID, team_id: uuid.UUID):
    stmt = delete(Subscription).where(
        Subscription.subscriber_id == subscriber_id,
        Subscription.team_id == team_id
    )
    await db.execute(stmt)
    await db.commit()

async def is_following(db: AsyncSession, subscriber_id: uuid.UUID, team_id: uuid.UUID) -> bool:
    stmt = select(Subscription).where(
        Subscription.subscriber_id == subscriber_id,
        Subscription.team_id == team_id
    )
    result = await db.execute(stmt)
    return result.scalars().first() is not None

async def toggle_follow_team(db: AsyncSession, subscriber_id: uuid.UUID, team_id: uuid.UUID) -> bool:
    if await is_following(db, subscriber_id, team_id):
        await unfollow_team(db, subscriber_id, team_id)
        return False
    else:
        await follow_team(db, subscriber_id, team_id)
        return True
