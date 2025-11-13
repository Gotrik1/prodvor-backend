# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

# Зависимости и CRUD
from app.dependencies import get_db, get_current_user, get_pagination, Pagination
from app import crud
from app.crud import crud_friend_request, crud_team, crud_user

# Схемы
from app.schemas.user import User, UserProfile, ProfileButton
from app.schemas.team import Team
from app.schemas.pagination import PaginatedResponse, PaginationMeta

# Модели
from app.models import FriendRequest, User as UserModel

def serialize_user(user: UserModel):
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

router = APIRouter()

async def get_profile_buttons(db: AsyncSession, current_user_id: UUID, profile_owner: UserModel) -> list[ProfileButton]:
    buttons = []
    if current_user_id == profile_owner.id:
        buttons.append(ProfileButton(action={"type": "edit_profile"}, text="Редактировать"))
    else:
        buttons.append(ProfileButton(action={"type": "write_message"}, text="Сообщение"))
    return buttons

@router.get("/me", response_model=UserProfile, operation_id="getCurrentUser")
async def read_users_me(db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user_profile = UserProfile.from_orm(current_user)
    user_profile.profile_buttons = await get_profile_buttons(db, current_user.id, current_user)
    return user_profile

@router.get("/{user_id}", response_model=UserProfile, operation_id="getUserById")
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    user = await crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = UserProfile.from_orm(user)
    user_profile.profile_buttons = await get_profile_buttons(db, current_user.id, user)
    return user_profile

@router.get("/{user_id}/friends")
async def list_user_friends(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(get_pagination),
):
    friend_ids = await crud.friend_request.get_friend_ids(db, user_id=user_id)
    total = len(friend_ids)

    start = pagination.offset
    end = start + pagination.limit
    page_ids = friend_ids[start:end] if friend_ids else []

    users = await crud.user.get_many_by_ids(db, page_ids)
    return {
        "meta": {"total": total, "limit": pagination.limit, "offset": pagination.offset},
        "data": [serialize_user(u) for u in users],
    }

@router.get("/{user_id}/followers", response_model=PaginatedResponse[User], operation_id="listUserFollowers")
async def read_user_followers(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    db: AsyncSession = Depends(get_db)
):
    meta = PaginationMeta(page=page, per_page=per_page, total=0, pages=0)
    return PaginatedResponse(data=[], meta=meta)

class FollowingUsersResponse(PaginatedResponse[User]):
    class Config:
        from_attributes = True

class FollowingTeamsResponse(PaginatedResponse[Team]):
    class Config:
        from_attributes = True

@router.get("/{user_id}/following", operation_id="listUserFollowing")
async def read_user_following(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skip = (page - 1) * per_page

    users, teams, total_users, total_teams = await crud_user.user.get_following_with_total(db, user_id=user.id, skip=skip, limit=per_page)
    meta_users = PaginationMeta(page=page, per_page=per_page, total=total_users, pages=(total_users + per_page - 1) // per_page)
    paginated_users = FollowingUsersResponse(data=users, meta=meta_users)

    meta_teams = PaginationMeta(page=page, per_page=per_page, total=total_teams, pages=(total_teams + per_page - 1) // per_page)
    paginated_teams = FollowingTeamsResponse(data=teams, meta=meta_teams)

    return {"users": paginated_users, "teams": paginated_teams}
