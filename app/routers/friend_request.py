# app/routers/friend_request.py
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
from app.schemas.pagination import PaginatedResponse
import uuid

router = APIRouter()

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

@router.put("/{request_id}/accept", response_model=schemas.FriendRequest)
async def accept_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found or you are not the receiver.")
    
    if friend_request.status != 'pending':
        raise HTTPException(status_code=400, detail="Friend request is not pending.")

    return await crud.friend_request.update(db=db, db_obj=friend_request, obj_in={"status": "accepted"})

@router.put("/{request_id}/decline", response_model=schemas.FriendRequest)
async def decline_friend_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found or you are not the receiver.")

    if friend_request.status != 'pending':
        raise HTTPException(status_code=400, detail="Friend request is not pending.")

    return await crud.friend_request.update(db=db, db_obj=friend_request, obj_in={"status": "declined"})

@router.get("/friends", response_model=PaginatedResponse[schemas.User])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, alias="page", ge=1),
    per_page: int = Query(10, alias="per_page", ge=1, le=100),
):
    skip = (page - 1) * per_page
    friends, total = await crud.friend_request.get_friends_with_total(db=db, user_id=current_user.id, skip=skip, limit=per_page)
    pages = math.ceil(total / per_page) if total > 0 else 0
    return PaginatedResponse(data=friends, meta={"total": total, "page": page, "per_page": per_page, "pages": pages})