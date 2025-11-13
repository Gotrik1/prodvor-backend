# app/crud/crud_user.py
import math
from typing import Optional, List, Tuple
import uuid
from sqlalchemy import func, or_, and_, delete, select, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import User, Team
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.models.subscription import Subscription
from app.models.user_team import UserTeam
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

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

    async def get_friends_with_total(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        fr = FriendRequest
        u = User

        # subquery со списком friend_id
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

        # считаем total
        total_q = select(func.count()).select_from(friend_ids_subq)
        total = (await db.execute(total_q)).scalar_one()

        # вытаскиваем пользователей по friend_id с пагинацией
        friends_q = (
            select(u)
            .where(u.id.in_(select(friend_ids_subq.c.friend_id)))
            .offset(skip)
            .limit(limit)
        )
        friends = (await db.execute(friends_q)).scalars().all()

        return friends, total

    async def get_followers_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[User], int]:
        return [], 0

    async def get_following_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[Team], int]:
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

        return teams, total

    async def get_many_by_ids(self, db: AsyncSession, ids: List[uuid.UUID]) -> List[User]:
        if not ids:
            return []
        res = await db.execute(select(User).where(User.id.in_(ids)))
        return list(res.scalars().all())

user = CRUDUser(User)
