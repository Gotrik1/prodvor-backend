# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel

# Зависимости и CRUD
from app.dependencies import get_db, get_current_user
from app import crud

# Схемы
from app.schemas.user import User, UserProfile, ProfileButton
from app.schemas.team import Team
from app.schemas.pagination import PaginatedResponse, PaginationMeta

# Модели
from app.models import FriendRequest

router = APIRouter()

# ... (get_profile_buttons)

def get_profile_buttons(db: Session, current_user_id: UUID, profile_owner: User) -> list[ProfileButton]:
    buttons = []
    if current_user_id == profile_owner.id:
        buttons.append(ProfileButton(action={"type": "edit_profile"}, text="Редактировать"))
    else:
        is_friend = any(friend.id == current_user_id for friend in profile_owner.friends)
        if is_friend:
            buttons.append(ProfileButton(action={"type": "friend_request", "status": "already_friend"}, text="Вы друзья"))
        else:
            sent_request = db.query(FriendRequest).filter_by(from_user_id=current_user_id, to_user_id=profile_owner.id, status='pending').first()
            received_request = db.query(FriendRequest).filter_by(from_user_id=profile_owner.id, to_user_id=current_user_id, status='pending').first()
            if sent_request:
                buttons.append(ProfileButton(action={"type": "friend_request", "status": "request_sent"}, text="Отменить заявку"))
            elif received_request:
                buttons.append(ProfileButton(action={"type": "friend_request", "status": "request_received"}, text="Принять заявку"))
            else:
                buttons.append(ProfileButton(action={"type": "friend_request", "status": "not_friend"}, text="Добавить в друзья"))
        buttons.append(ProfileButton(action={"type": "write_message"}, text="Сообщение"))
    buttons.append(ProfileButton(action={"type": "more_options"}, text="..."))
    return buttons

@router.get("/me", response_model=UserProfile, operation_id="getCurrentUser")
def read_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_profile = UserProfile.from_orm(current_user)
    user_profile.profile_buttons = get_profile_buttons(db, current_user.id, current_user)
    return user_profile

@router.get("/{user_id}", response_model=UserProfile, operation_id="getUserById")
def read_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_profile = UserProfile.from_orm(user)
    user_profile.profile_buttons = get_profile_buttons(db, current_user.id, user)
    return user_profile

@router.get("/{user_id}/friends", response_model=PaginatedResponse[User], operation_id="listUserFriends")
def read_user_friends(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    skip = (page - 1) * per_page
    friends = crud.user.get_friends(db, user=user, skip=skip, limit=per_page)
    total = user.friends.count()
    
    meta = PaginationMeta(page=page, per_page=per_page, total=total, pages=(total + per_page - 1) // per_page)
    return PaginatedResponse(data=friends, meta=meta)

@router.get("/{user_id}/followers", response_model=PaginatedResponse[User], operation_id="listUserFollowers")
def read_user_followers(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skip = (page - 1) * per_page
    followers = crud.user.get_followers(db, user=user, skip=skip, limit=per_page)
    total = user.followers.count()

    meta = PaginationMeta(page=page, per_page=per_page, total=total, pages=(total + per_page - 1) // per_page)
    return PaginatedResponse(data=followers, meta=meta)

# Модель ответа для эндпоинта following
class FollowingResponse(BaseModel):
    users: PaginatedResponse[User]
    teams: PaginatedResponse[Team]

@router.get("/{user_id}/following", response_model=FollowingResponse, operation_id="listUserFollowing")
def read_user_following(
    user_id: UUID,
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Элементов на странице"),
    db: Session = Depends(get_db)
):
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skip = (page - 1) * per_page

    # Пагинация для пользователей
    following_users = crud.user.get_following_users(db, user=user, skip=skip, limit=per_page)
    total_users = user.followingUsers.count()
    meta_users = PaginationMeta(page=page, per_page=per_page, total=total_users, pages=(total_users + per_page - 1) // per_page)
    paginated_users = PaginatedResponse(data=following_users, meta=meta_users)

    # Пагинация для команд
    following_teams = crud.user.get_following_teams(db, user=user, skip=skip, limit=per_page)
    total_teams = len(user.followingTeams) # .count() не работает для этого отношения
    meta_teams = PaginationMeta(page=page, per_page=per_page, total=total_teams, pages=(total_teams + per_page - 1) // per_page)
    paginated_teams = PaginatedResponse(data=following_teams, meta=meta_teams)

    return FollowingResponse(users=paginated_users, teams=paginated_teams)
