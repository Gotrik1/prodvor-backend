from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
import uuid

router = APIRouter()

@router.post("", response_model=schemas.FriendRequest, dependencies=[Depends(get_current_user)])
def create_friend_request(
    *, 
    db: Session = Depends(get_db),
    friend_request_in: schemas.FriendRequestCreate,
    current_user: models.User = Depends(get_current_user)
):
    # Prevent users from sending a friend request to themselves
    if current_user.id == friend_request_in.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself.")
    
    # Check if a friend request already exists
    existing_request = crud.friend_request.get_friend_request_by_users(db=db, requester_id=current_user.id, receiver_id=friend_request_in.receiver_id)
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent.")

    return crud.friend_request.create_friend_request(db=db, obj_in=friend_request_in, requester_id=current_user.id)

@router.get("/received", response_model=list[schemas.FriendRequest], dependencies=[Depends(get_current_user)])
def get_received_friend_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.friend_request.get_received_friend_requests(db=db, user_id=current_user.id)

@router.put("/{request_id}/accept", response_model=schemas.FriendRequest, dependencies=[Depends(get_current_user)])
def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found.")
    
    return crud.friend_request.accept_friend_request(db=db, request_id=request_id)

@router.put("/{request_id}/decline", response_model=schemas.FriendRequest, dependencies=[Depends(get_current_user)])
def decline_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    friend_request = crud.friend_request.get(db, id=request_id)
    if not friend_request or friend_request.receiver_id != current_user.id:
        raise HTTPException(status_code=404, detail="Friend request not found.")

    return crud.friend_request.decline_friend_request(db=db, request_id=request_id)

@router.get("/friends", response_model=list[schemas.User], dependencies=[Depends(get_current_user)])
def get_friends(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.friend_request.get_friends(db=db, user_id=current_user.id)
