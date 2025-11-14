
import uuid
from typing import List, Tuple
from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import crud
from app.models import User, Team, FriendRequest, Subscription, UserTeam
from app.models.friend_request import FriendRequestStatus

class UserService:
    async def get_user_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User:
        user = await crud.user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_friends(
        self, db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
    ) -> Tuple[List[User], int]:
        # This logic was originally in crud_user.py
        fr = FriendRequest
        u = User

        friend_ids_subq = (
            select(
                func.coalesce(
                    func.nullif(fr.receiver_id, user_id),
                    fr.requester_id
                ).label("friend_id")
            )
            .where(
                fr.status == FriendRequestStatus.accepted,
                or_(fr.requester_id == user_id, fr.receiver_id == user_id),
            )
        ).subquery()

        total_q = select(func.count()).select_from(friend_ids_subq)
        total = (await db.execute(total_q)).scalar_one()

        friends_q = (
            select(u)
            .where(u.id.in_(select(friend_ids_subq.c.friend_id)))
            .offset(offset)
            .limit(limit)
        )
        friends_res = await db.execute(friends_q)
        friends = list(friends_res.scalars().all())

        return friends, total

    async def get_user_followers(
        self, db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
    ) -> Tuple[List[User], int]:
        # This is a placeholder as the original was empty. 
        # In a real scenario, we would query subscriptions to this user.
        return [], 0

    async def get_user_following(
        self, db: AsyncSession, user_id: uuid.UUID, limit: int, offset: int
    ) -> Tuple[List[Team], int]:
        # This logic was originally in crud_user.py
        ids_res = await db.execute(
            select(Subscription.team_id).where(Subscription.user_id == user_id)
        )
        ids = [row[0] for row in ids_res.all()]
        total = len(ids)

        page_ids = ids[offset:offset + limit]

        if not page_ids:
            teams = []
        else:
            teams_res = await db.execute(
                select(Team)
                .where(Team.id.in_(page_ids))
                .options(selectinload(Team.member_associations).selectinload(UserTeam.user))
            )
            teams = list(teams_res.scalars().unique().all())

        return teams, total

user_service = UserService()
