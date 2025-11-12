# app/crud/crud_friend_request.py
from typing import List, Optional, Tuple
import uuid

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import FriendRequest, User
from app.schemas.friend_request import FriendRequestCreate, FriendRequestUpdate


class CRUDFriendRequest(CRUDBase[FriendRequest, FriendRequestCreate, FriendRequestUpdate]):
    async def get_friend_request_by_users(
        self, db: AsyncSession, *, requester_id: uuid.UUID, receiver_id: uuid.UUID
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
        self, db: AsyncSession, *, obj_in: FriendRequestCreate, requester_id: uuid.UUID
    ) -> FriendRequest:
        db_obj = self.model(
            **obj_in.model_dump(), requester_id=requester_id, status="pending"
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_received(self, db: AsyncSession, *, user_id: uuid.UUID) -> List[FriendRequest]:
        result = await db.execute(
            select(self.model)
            .where(self.model.receiver_id == user_id, self.model.status == "pending")
        )
        return result.scalars().all()

    async def get_friends_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[User], int]:
        # Get friends where the user is the requester
        requester_friends_query = select(User).join(FriendRequest, User.id == FriendRequest.receiver_id) \
            .where(FriendRequest.requester_id == user_id, FriendRequest.status == "accepted")
        
        requester_friends_result = await db.execute(requester_friends_query)
        requester_friends = requester_friends_result.scalars().all()
        
        # Get friends where the user is the receiver
        receiver_friends_query = select(User).join(FriendRequest, User.id == FriendRequest.requester_id) \
            .where(FriendRequest.receiver_id == user_id, FriendRequest.status == "accepted")
        
        receiver_friends_result = await db.execute(receiver_friends_query)
        receiver_friends = receiver_friends_result.scalars().all()

        # Combine, deduplicate, and paginate
        all_friends = {friend.id: friend for friend in requester_friends + receiver_friends}.values()
        
        total = len(all_friends)
        paginated_friends = list(all_friends)[skip : skip + limit]
        
        return paginated_friends, total

friend_request = CRUDFriendRequest(FriendRequest)
