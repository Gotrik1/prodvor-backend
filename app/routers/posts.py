from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("", response_model=schemas.Post)
async def create_post(
    *, 
    db: AsyncSession = Depends(get_db),
    post_in: schemas.PostCreate,
    current_user: models.User = Depends(get_current_user)
):
    return await crud.post.create_with_author(db=db, obj_in=post_in, author_id=current_user.id)

@router.get("/{post_id}", response_model=schemas.Post)
async def read_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    post = await crud.post.get(db=db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("", response_model=List[schemas.Post])
async def read_posts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return await crud.post.get_multi(db, skip=skip, limit=limit)

@router.put("/{post_id}", response_model=schemas.Post)
async def update_post(
    *,
    db: AsyncSession = Depends(get_db),
    post_id: UUID,
    post_in: schemas.PostUpdate,
    current_user: models.User = Depends(get_current_user)
):
    post = await crud.post.get(db=db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.post.update(db=db, db_obj=post, obj_in=post_in)

@router.delete("/{post_id}", response_model=schemas.Post)
async def delete_post(
    *,
    db: AsyncSession = Depends(get_db),
    post_id: UUID,
    current_user: models.User = Depends(get_current_user)
):
    post = await crud.post.get(db=db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.post.remove(db=db, id=post_id)
