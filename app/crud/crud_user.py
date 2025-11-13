# app/crud/crud_user.py
import math
from typing import Optional, List, Tuple
import uuid
from sqlalchemy import func, or_, and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import User, Team
from app.models.friend_request import FriendRequest
from app.models.subscription import Subscription
from app.models.user_team import UserTeam
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            nickname=obj_in.nickname,
            birth_date=obj_in.birth_date,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def list_friends(self, db, user_id: uuid.UUID) -> list[User]:
        q = (
            select(User)
            .where(
                or_(
                    and_(
                        FriendRequest.requester_id == user_id,
                        User.id == FriendRequest.receiver_id,
                    ),
                    and_(
                        FriendRequest.receiver_id == user_id,
                        User.id == FriendRequest.requester_id,
                    ),
                ),
            )
            .join(FriendRequest, or_(
                FriendRequest.requester_id == User.id,
                FriendRequest.receiver_id == User.id,
            ))
            .where(FriendRequest.status == 'accepted')
        )
        res = await db.execute(q)
        return list(res.scalars().unique())

    async def are_friends(self, db, user1_id: str, user2_id: str) -> bool:
        q = select(FriendRequest).where(
            or_(
                and_(FriendRequest.requester_id == user1_id, FriendRequest.receiver_id == user2_id),
                and_(FriendRequest.requester_id == user2_id, FriendRequest.receiver_id == user1_id),
            ),
            FriendRequest.status == 'accepted',
        )
        res = await db.execute(q)
        return res.scalar_one_or_none() is not None

    async def get_followers_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[User], int]:
        return [], 0

    async def get_following_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[User], List[Team], int, int]:
        ids_res = await db.execute(
            select(Subscription.team_id).where(Subscription.user_id == user_id)
        )
        ids = [row[0] for row in ids_res.all()]
        total = len(ids)

        start = skip
        end = skip + limit
        page_ids = ids[start:end]

        if not page_ids:
            teams = []
        else:
            teams_res = await db.execute(
                select(Team)
                .where(Team.id.in_(page_ids))
                .options(selectinload(Team.member_associations).selectinload(UserTeam.user))
            )
            teams = teams_res.scalars().unique().all()

        return [], teams, 0, total
    
    async def is_following_team(self, db: AsyncSession, *, user_id: uuid.UUID, team_id: uuid.UUID) -> bool:
        result = await db.execute(
            select(Subscription).filter(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.team_id == team_id
                )
            )
        )
        return result.scalars().first() is not None

    async def follow_team(self, db: AsyncSession, *, user_id: uuid.UUID, team_id: uuid.UUID) -> None:
        # This logic is now a toggle in the router, but leaving the basic function here
        if not await self.is_following_team(db, user_id=user_id, team_id=team_id):
            subscription = Subscription(user_id=user_id, team_id=team_id)
            db.add(subscription)
            await db.commit()

    async def unfollow_team(self, db: AsyncSession, *, user_id: uuid.UUID, team_id: uuid.UUID) -> None:
        stmt = delete(Subscription).where(
            and_(
                Subscription.user_id == user_id,
                Subscription.team_id == team_id
            )
        )
        await db.execute(stmt)
        await db.commit()

    async def get_friends_with_total(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
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
                fr.status == "accepted",
                or_(fr.requester_id == user_id, fr.receiver_id == user_id),
            )
        ).subquery()

        total_q = select(func.count()).select_from(friend_ids_subq)
        total = (await db.execute(total_q)).scalar_one()

        friends_q = (
            select(u)
            .where(u.id.in_(select(friend_ids_subq.c.friend_id)))
            .offset(skip)
            .limit(limit)
        )
        friends = (await db.execute(friends_q)).scalars().all()

        return friends, total

    async def get_many_by_ids(self, db: AsyncSession, ids: List[uuid.UUID]) -> List[User]:
        if not ids:
            return []
        res = await db.execute(select(User).where(User.id.in_(ids)))
        return list(res.scalars().all())

user = CRUDUser(User)
