from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("", response_model=schemas.Comment)
async def create_comment(
    *, 
    db: AsyncSession = Depends(get_db),
    comment_in: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user)
):
    # Проверка существования поста
    post = await crud.post.get(db, id=comment_in.postId)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return await crud.comment.create_with_author(db=db, obj_in=comment_in, author_id=current_user.id)

@router.get("/{comment_id}", response_model=schemas.Comment)
async def read_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    comment = await crud.comment.get(db=db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.get("/post/{post_id}", response_model=List[schemas.Comment])
async def read_comments_for_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    # Проверка существования поста
    post = await crud.post.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return await crud.comment.get_multi_by_post(db, post_id=post_id, skip=skip, limit=limit)

@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    *,
    db: AsyncSession = Depends(get_db),
    comment_id: UUID,
    comment_in: schemas.CommentUpdate,
    current_user: models.User = Depends(get_current_user)
):
    comment = await crud.comment.get(db=db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.authorId != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.comment.update(db=db, db_obj=comment, obj_in=comment_in)

@router.delete("/{comment_id}", response_model=schemas.Comment)
async def delete_comment(
    *,
    db: AsyncSession = Depends(get_db),
    comment_id: UUID,
    current_user: models.User = Depends(get_current_user)
):
    comment = await crud.comment.get(db=db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.authorId != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud.comment.remove(db=db, id=comment_id)
