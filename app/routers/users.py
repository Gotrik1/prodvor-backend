from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.dependencies import get_db, get_current_user, get_pagination
from app.models import User
from app.schemas.pagination import Pagination

router = APIRouter()

def serialize_user(user: User) -> schemas.User:
    return schemas.User.from_orm(user)

@router.get("/me", response_model=schemas.UserProfile)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserProfile)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await crud.user.get(db, id=user_id)

@router.get("/{user_id}/friends")
async def read_user_friends(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    friends, total = await crud.user.get_friends_with_total(
        db, user_id=user_id, skip=pagination.offset, limit=pagination.limit
    )
    return {
        "meta": {"total": total, "limit": pagination.limit, "offset": pagination.offset},
        "data": [serialize_user(u) for u in friends],
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

    # In the future, we might follow users as well
    # For now, we only support following teams
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
