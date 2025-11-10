
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas, models
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas.post.Post])
def read_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve posts.
    """
    posts = crud.post.get_multi(db, skip=skip, limit=limit)
    return posts

@router.post("", response_model=schemas.post.Post)
def create_post(
    *,
    db: Session = Depends(get_db),
    post_in: schemas.post.PostCreate,
    current_user: models.User = Depends(get_current_user),
):
    """
    Create new post.
    """
    post = crud.post.create(db, obj_in=post_in, author_id=current_user.id)
    return post
