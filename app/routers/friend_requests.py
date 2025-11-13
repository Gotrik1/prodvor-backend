# app/routers/friend_requests.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.dependencies import get_db, get_current_user, get_pagination, Pagination
from app import crud, schemas
from app.models.friend_request import FriendRequestStatus
from app.schemas.pagination import PaginatedResponse
from app.schemas.user import User

router = APIRouter()

def serialize_user(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "birth_date": str(user.birth_date),
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }

@router.post("", response_model=schemas.friend_request.FriendRequest)
async def create_friend_request(
    *, 
    db: AsyncSession = Depends(get_db), 
    friend_request_in: schemas.friend_request.FriendRequestCreate, 
    current_user: schemas.user.User = Depends(get_current_user)
):
    if friend_request_in.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    existing_request = await crud.friend_request.get_friend_request_by_users(
        db, requester_id=current_user.id, receiver_id=friend_request_in.receiver_id
    )
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already exists")

    return await crud.friend_request.create_with_requester(
        db, obj_in=friend_request_in, requester_id=current_user.id
    )

@router.get("/received", response_model=list[schemas.friend_request.FriendRequest])
async def get_received_friend_requests(
    db: AsyncSession = Depends(get_db), current_user: schemas.user.User = Depends(get_current_user)
):
    return await crud.friend_request.get_received(db, user_id=current_user.id)


@router.get("/", response_model=PaginatedResponse[User])
async def get_friends(
    db: AsyncSession = Depends(get_db), 
    current_user: schemas.user.User = Depends(get_current_user),
    pagination: Pagination = Depends(get_pagination)
):
    friend_ids = await crud.friend_request.get_friend_ids(db, user_id=current_user.id)
    
    total = len(friend_ids)
    start = pagination.offset
    end = start + pagination.limit
    paginated_ids = friend_ids[start:end]
    
    friends = await crud.user.get_many_by_ids(db, paginated_ids)
    
    return {
        "meta": {"total": total, "limit": pagination.limit, "offset": pagination.offset},
        "data": [serialize_user(u) for u in friends]
    }

@router.put("/{request_id}/accept")
async def accept_friend_request(request_id: UUID, db: AsyncSession = Depends(get_db), current_user: schemas.user.User = Depends(get_current_user)):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")

    friend_request.status = FriendRequestStatus.accepted
    await db.commit()
    return {"message": "Friend request accepted"}

@router.put("/{request_id}/decline")
async def decline_friend_request(request_id: UUID, db: AsyncSession = Depends(get_db), current_user: schemas.user.User = Depends(get_current_user)):
    friend_request = await crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found")

    await db.delete(friend_request)
    await db.commit()
    return {"message": "Friend request declined"}


