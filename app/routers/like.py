from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
import uuid

router = APIRouter()

@router.post("", response_model=schemas.Like)
async def create_like(
    *, 
    db: AsyncSession = Depends(get_db),
    like_in: schemas.LikeCreateRequest,  # Use the new request schema
    current_user: models.User = Depends(get_current_user)
):
    # Check if the user has already liked the post
    existing_like = await crud.like.get_by_user_and_post(db, user_id=current_user.id, post_id=like_in.post_id)
    if existing_like:
        raise HTTPException(status_code=400, detail="You have already liked this post")
    
    # Create the full LikeCreate object
    full_like_in = schemas.LikeCreate(user_id=current_user.id, post_id=like_in.post_id)
    
    return await crud.like.create(db=db, obj_in=full_like_in) # Use the base create method

@router.delete("/{post_id}", response_model=schemas.Like)
async def delete_like(
    *,
    db: AsyncSession = Depends(get_db),
    post_id: uuid.UUID,
    current_user: models.User = Depends(get_current_user)
):
    like = await crud.like.get_by_user_and_post(db, user_id=current_user.id, post_id=post_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    # The CRUDBase expects the model instance to remove, not just the ID.
    # So we pass the `like` object we just fetched.
    return await crud.like.remove(db=db, id=like.id)

@router.get("/post/{post_id}/count", response_model=schemas.LikeCount)
async def get_like_count_for_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    count = await crud.like.get_like_count_for_post(db, post_id=post_id)
    return {"count": count}

@router.get("/user/{user_id}/liked-posts", response_model=list[schemas.Post])
async def get_liked_posts_by_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    return await crud.like.get_liked_posts_by_user(db, user_id=user_id)
