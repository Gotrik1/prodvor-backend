from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.dependencies import get_db, get_current_user, get_pagination, Pagination
from app.models import User

def serialize_user(user: User) -> schemas.User:
    return schemas.User.from_orm(user)

router = APIRouter()

@router.get("/me", response_model=schemas.UserProfile)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserProfile)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/friends")
async def list_user_friends(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    friend_ids = await crud.friend_request.get_friend_ids(db, user_id=user_id)
    total = len(friend_ids)

    paginated_ids = friend_ids[pagination.offset : pagination.offset + pagination.limit]

    if paginated_ids:
        friends = await crud.user.get_many_by_ids(db, ids=paginated_ids)
    else:
        friends = []

    id_map = {user.id: user for user in friends}
    ordered_friends = [id_map[id] for id in paginated_ids if id in id_map]

    return {
        "meta": {
            "total": total,
            "limit": pagination.limit,
            "offset": pagination.offset,
        },
        "data": [serialize_user(u) for u in ordered_friends],
    }

@router.get("/{user_id}/followers")
async def read_user_followers(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    followers, total = await crud.user.get_followers_with_total(
        db, user_id=user_id, skip=pagination.offset, limit=pagination.limit
    )
    return {
        "meta": {"total": total, "limit": pagination.limit, "offset": pagination.offset},
        "data": [serialize_user(u) for u in followers],
    }

@router.get("/{user_id}/following")
async def read_user_following(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    following_teams, total_teams = await crud.user.get_following_with_total(
        db, user_id=user_id, skip=pagination.offset, limit=pagination.limit
    )

    return {
        "users": {
            "meta": {"total": 0, "limit": pagination.limit, "offset": pagination.offset},
            "data": [],
        },
        "teams": {
            "meta": {"total": total_teams, "limit": pagination.limit, "offset": pagination.offset},
            "data": following_teams,
        }
    }
