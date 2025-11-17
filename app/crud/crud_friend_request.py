# app/crud/crud_friend_request.py
from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, or_, and_, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models import FriendRequest, User
from app.schemas.friend_request import FriendRequestCreate, FriendRequestUpdate
from app.models.friend_request import FriendRequestStatus

class CRUDFriendRequest(CRUDBase[FriendRequest, FriendRequestCreate, FriendRequestUpdate]):
    async def get_friend_request_by_users(
        self, db: AsyncSession, *, requester_id: UUID, receiver_id: UUID
    ) -> Optional[FriendRequest]:
        result = await db.execute(
            select(self.model).where(
                or_(
                    and_(self.model.requester_id == requester_id, self.model.receiver_id == receiver_id),
                    and_(self.model.requester_id == receiver_id, self.model.receiver_id == requester_id),
                )
            )
        )
        return result.scalars().first()

    async def create_with_requester(
        self, db: AsyncSession, *, obj_in: FriendRequestCreate, requester_id: UUID
    ) -> FriendRequest:
        db_obj = self.model(receiver_id=obj_in.receiver_id, requester_id=requester_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_received(self, db: AsyncSession, *, user_id: UUID) -> list[FriendRequest]:
        result = await db.execute(
            select(self.model).where(self.model.receiver_id == user_id, self.model.status == FriendRequestStatus.pending)
        )
        return result.scalars().all()
    
    async def get_friend_ids(self, db: AsyncSession, *, user_id: UUID) -> List[UUID]:
        stmt = (
            select(self.model.requester_id, self.model.receiver_id)
            .where(
                or_(
                    self.model.requester_id == user_id,
                    self.model.receiver_id == user_id,
                ),
                self.model.status == FriendRequestStatus.accepted,
            )
        )

        result = await db.execute(stmt)
        friend_ids = set()
        for requester_id, receiver_id in result.all():
            if requester_id == user_id:
                friend_ids.add(receiver_id)
            else:
                friend_ids.add(requester_id)
        
        return list(friend_ids)

    async def get_followers_with_total(
        self, db: AsyncSession, *, user_id: UUID, skip: int, limit: int
    ) -> tuple[list[User], int]:
        # Query for total count of followers
        total_query = (
            select(func.count(self.model.requester_id))
            .where(self.model.receiver_id == user_id)
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar_one_or_none() or 0

        # Query for paginated followers' User objects
        followers_query = (
            select(User)
            .join(self.model, User.id == self.model.requester_id)
            .where(self.model.receiver_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        followers_result = await db.execute(followers_query)
        followers = followers_result.scalars().all()

        return followers, total

friend_request = CRUDFriendRequest(FriendRequest)
