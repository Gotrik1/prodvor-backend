# app/routers/subscriptions.py
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_user
from app import crud
from sqlalchemy import select
from app.models import Subscription

router = APIRouter()

class SubscribeRequest(BaseModel):
    team_id: UUID4

@router.post("/subscribe", status_code=204)
async def subscribe(req: SubscribeRequest,
                    db: AsyncSession = Depends(get_db),
                    current_user = Depends(get_current_user)):
    await crud.subscription.subscribe(
        db=db, user_id=current_user.id, team_id=req.team_id
    )
    return Response(status_code=204)

@router.post("/unsubscribe", status_code=204)
async def unsubscribe(req: SubscribeRequest,
                      db: AsyncSession = Depends(get_db),
                      current_user = Depends(get_current_user)):
    await crud.subscription.unsubscribe(
        db=db, user_id=current_user.id, team_id=req.team_id
    )
    return Response(status_code=204)

@router.get("/status")
async def status(team_id: UUID4 = Query(...),
                 db: AsyncSession = Depends(get_db),
                 current_user = Depends(get_current_user)):
    is_following = await crud.subscription.get_subscription_status(db=db, user_id=current_user.id, team_id=team_id)
    return {"is_following": is_following}

@router.get("/notifications")
async def get_notification_history(db: AsyncSession = Depends(get_db),
                                   current_user = Depends(get_current_user)):
    # имя функции должно существовать в crud_notification
    return await crud.notification.get_notifications_for_user(
        db, user_id=current_user.id
    )
