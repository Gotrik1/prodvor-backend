# app/routers/friend_request.py
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user, get_pagination, Pagination
from app.schemas.pagination import PaginatedResponse
import uuid
from app.models.friend_request import FriendRequestStatus

router = APIRouter()

def serialize_user(user: models.User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "birth_date": str(user.birth_date),
    }

@router.post("", response_model=schemas.FriendRequest)
async def create_friend_request(
    *, 
    db: AsyncSession = Depends(get_db),
    friend_request_in: schemas.FriendRequestCreate,
    current_user: models.User = Depends(get_current_user)
):
    # Prevent users from sending a friend request to themselves
    if current_user.id == friend_request_in.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself.")
    
    # Check if a friend request already exists between the two users
    existing_request = await crud.friend_request.get_friend_request_by_users(db=db, requester_id=current_user.id, receiver_id=friend_request_in.receiver_id)
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent or received.")

    return await crud.friend_request.create_with_requester(db=db, obj_in=friend_request_in, requester_id=current_user.id)

@router.get("/received", response_model=list[schemas.FriendRequest])
async def get_received_friend_requests(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.friend_request.get_received(db=db, user_id=current_user.id)

@router.get("/friends")
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    pagination: Pagination = Depends(get_pagination),
):
    # Все id друзей текущего пользователя
    friend_ids = await crud.friend_request.get_friend_ids(db, user_id=current_user.id)

    total = len(friend_ids)
    start = pagination.offset
    end = start + pagination.limit
    page_ids = friend_ids[start:end]

    friends = await crud.user.get_many_by_ids(db, ids=page_ids)

    return {
        "meta": {
            "total": total,
            "limit": pagination.limit,
            "offset": pagination.offset,
        },
        "data": [serialize_user(u) for u in friends],
    }

@router.put("/{request_id}/accept", response_model=schemas.FriendRequest)
async def accept_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found or you are not the receiver.")
    
    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Friend request is not pending.")

    friend_request.status = FriendRequestStatus.accepted
    await db.flush()
    await db.commit()
    return friend_request

@router.put("/{request_id}/decline", response_model=schemas.FriendRequest)
async def decline_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found or you are not the receiver.")

    if friend_request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=400, detail="Friend request is not pending.")

    return await crud.friend_request.update(db=db, db_obj=friend_request, obj_in={"status": FriendRequestStatus.declined})
