from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.dependencies import get_db, get_current_user
from app.schemas.subscription import SubscriptionCreate
from app.schemas.notification import Notification
from app.crud import crud_subscription, crud_notification

router = APIRouter()

@router.post("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
def subscribe(sub_in: SubscriptionCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = uuid.UUID(current_user["id"])
    # TODO: Here we should probably create a notification for all team followers that a new user has subscribed
    crud_subscription.follow_team(db, user_id=user_id, team_id=sub_in.team_id)

@router.post("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(sub_in: SubscriptionCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = uuid.UUID(current_user["id"])
    crud_subscription.unfollow_team(db, user_id=user_id, team_id=sub_in.team_id)

@router.get("/status", response_model=dict)
def get_subscription_status(team_id: uuid.UUID = Query(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = uuid.UUID(current_user["id"])
    is_following = crud_subscription.is_following(db, user_id=user_id, team_id=team_id)
    return {"is_following": is_following}

@router.get("/notifications", response_model=List[Notification])
def get_notification_history(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = uuid.UUID(current_user["id"])
    return crud_notification.get_notifications_for_user(db, user_id=user_id)
