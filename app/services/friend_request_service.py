
import uuid
from typing import List, Tuple
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.schemas.friend_request import FriendRequestCreate
from app.models.friend_request import FriendRequestStatus


class FriendRequestService:
    async def create_friend_request(
        self, db: AsyncSession, *, requester_id: uuid.UUID, request_in: FriendRequestCreate
    ) -> models.FriendRequest:
        if requester_id == request_in.receiver_id:
            raise HTTPException(
                status_code=400, detail="Cannot send a friend request to yourself."
            )

        existing_request = await crud.friend_request.get_friend_request_by_users(
            db=db, requester_id=requester_id, receiver_id=request_in.receiver_id
        )
        if existing_request:
            raise HTTPException(
                status_code=400, detail="Friend request already sent or received."
            )

        return await crud.friend_request.create_with_requester(
            db=db, obj_in=request_in, requester_id=requester_id
        )

    async def get_received_requests(
        self, db: AsyncSession, *, user_id: uuid.UUID
    ) -> List[models.FriendRequest]:
        return await crud.friend_request.get_received(db=db, user_id=user_id)

    async def accept_friend_request(
        self, db: AsyncSession, *, request_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> models.FriendRequest:
        friend_request = await crud.friend_request.get(db, id=request_id)
        if not friend_request or friend_request.receiver_id != current_user_id:
            raise HTTPException(
                status_code=404, detail="Friend request not found or you are not the receiver."
            )

        if friend_request.status != FriendRequestStatus.pending:
            raise HTTPException(status_code=400, detail="Friend request is not pending.")

        friend_request.status = FriendRequestStatus.accepted
        await db.flush()
        await db.commit()
        return friend_request

    async def decline_friend_request(
        self, db: AsyncSession, *, request_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> models.FriendRequest:
        friend_request = await crud.friend_request.get(db, id=request_id)
        if not friend_request or friend_request.receiver_id != current_user_id:
            raise HTTPException(
                status_code=404, detail="Friend request not found or you are not the receiver."
            )

        if friend_request.status != FriendRequestStatus.pending:
            raise HTTPException(status_code=400, detail="Friend request is not pending.")

        return await crud.friend_request.update(
            db=db, db_obj=friend_request, obj_in={"status": FriendRequestStatus.declined}
        )

friend_request_service = FriendRequestService()
