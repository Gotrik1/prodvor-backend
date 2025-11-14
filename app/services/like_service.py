
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
import uuid

class LikeService:
    async def create_like(self, db: AsyncSession, *, post_id: uuid.UUID, user_id: uuid.UUID) -> models.Like:
        existing_like = await crud.like.get_by_user_and_post(db, user_id=user_id, post_id=post_id)
        if existing_like:
            raise HTTPException(status_code=400, detail="You have already liked this post")
        
        like_in = schemas.LikeCreate(user_id=user_id, post_id=post_id)
        return await crud.like.create(db=db, obj_in=like_in)

    async def delete_like(self, db: AsyncSession, *, post_id: uuid.UUID, user_id: uuid.UUID) -> models.Like:
        like = await crud.like.get_by_user_and_post(db, user_id=user_id, post_id=post_id)
        if not like:
            raise HTTPException(status_code=404, detail="Like not found")
        
        return await crud.like.remove(db=db, id=like.id)

    async def get_like_count_for_post(self, db: AsyncSession, *, post_id: uuid.UUID) -> int:
        return await crud.like.get_like_count_for_post(db, post_id=post_id)

    async def get_liked_posts_by_user(self, db: AsyncSession, *, user_id: uuid.UUID) -> list[models.Post]:
        return await crud.like.get_liked_posts_by_user(db, user_id=user_id)

like_service = LikeService()
