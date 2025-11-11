from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Like)
def create_like(
    *, 
    db: Session = Depends(get_db),
    like_in: schemas.LikeCreate,
    current_user: models.User = Depends(get_current_user)
):
    # Check if the user has already liked the post
    existing_like = crud.like.get_by_user_and_post(db, user_id=current_user.id, post_id=like_in.post_id)
    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this post")
    return crud.like.create_with_user_and_post(db=db, obj_in=like_in, user_id=current_user.id, post_id=like_in.post_id)

@router.delete("/{post_id}", response_model=schemas.Like)
def delete_like(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    current_user: models.User = Depends(get_current_user)
):
    like = crud.like.get_by_user_and_post(db, user_id=current_user.id, post_id=post_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    return crud.like.remove(db=db, id=like.id)

@router.get("/post/{post_id}/count", response_model=int)
def get_like_count_for_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    return crud.like.get_like_count_for_post(db, post_id=post_id)

@router.get("/user/{user_id}/liked-posts", response_model=list[schemas.Post])
def get_liked_posts_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return crud.like.get_liked_posts_by_user(db, user_id=user_id)
