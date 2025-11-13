# app/crud/crud_friend_request.py
from uuid import UUID
from typing import Optional, List
from sqlalchemy import select, or_, and_, union_all, distinct
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
        db_obj = self.model(**obj_in.model_dump(), requester_id=requester_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_received(self, db: AsyncSession, *, user_id: UUID) -> list[FriendRequest]:
        result = await db.execute(
            select(self.model).where(self.model.receiver_id == user_id, self.model.status == FriendRequestStatus.pending)
        )
        return result.scalars().all()
    
    async def get_friend_ids(self, db: AsyncSession, *, user_id: UUID) -> list[UUID]:
        accepted = FriendRequestStatus.accepted

        q1 = select(FriendRequest.receiver_id.label("friend_id")).where(
            FriendRequest.requester_id == user_id, FriendRequest.status == accepted
        )
        q2 = select(FriendRequest.requester_id.label("friend_id")).where(
            FriendRequest.receiver_id == user_id, FriendRequest.status == accepted
        )
        
        union_stmt = union_all(q1, q2)
        stmt = select(distinct(union_stmt.c.friend_id))
        
        result = await db.execute(stmt)
        return result.scalars().all()

friend_request = CRUDFriendRequest(FriendRequest)
