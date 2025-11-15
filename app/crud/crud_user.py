# app/crud/crud_user.py
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models import User, Team, team_followers
from app.models.friend_request import FriendRequest, FriendRequestStatus
from app.models.subscription import Subscription
from app.models.user_team import UserTeam
from app.schemas.user import UserCreate, UserCreateDB, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        statement = select(self.model).where(self.model.email == email)
        return (await db.execute(statement)).scalar_one_or_none()

    async def get_many_by_ids(self, db: AsyncSession, *, ids: list[UUID]) -> list[User]:
        statement = select(self.model).where(self.model.id.in_(ids))
        return (await db.execute(statement)).scalars().all()

    async def get_following_with_total(
        self, db: AsyncSession, *, user_id: UUID, skip: int, limit: int
    ) -> tuple[list[Team], int]:
        # Запрос для получения команд, на которые подписан пользователь
        query = (
            select(Team)
            .join(team_followers)
            .where(team_followers.c.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        teams_result = await db.execute(query)
        teams = teams_result.scalars().all()

        # Запрос для получения общего количества подписок
        total_query = (
            select(func.count())
            .select_from(team_followers)
            .where(team_followers.c.user_id == user_id)
        )
        total = await db.scalar(total_query)

        return teams, total or 0

    async def create(self, db: AsyncSession, *, obj_in: UserCreateDB) -> User:
        db_obj = User(
            email=obj_in.email,
            nickname=obj_in.nickname,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            birth_date=obj_in.birth_date,
            hashed_password=obj_in.password, 
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)
