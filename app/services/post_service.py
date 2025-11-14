
import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.schemas.post import PostCreate, PostUpdate

class PostService:
    async def create_post(
        self, db: AsyncSession, *, author_id: uuid.UUID, post_in: PostCreate
    ) -> models.Post:
        return await crud.post.create_with_author(
            db=db, obj_in=post_in, author_id=author_id
        )

    async def get_post(self, db: AsyncSession, *, post_id: uuid.UUID) -> models.Post:
        post = await crud.post.get(db=db, id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    async def get_posts(
        self, db: AsyncSession, *, skip: int, limit: int
    ) -> List[models.Post]:
        return await crud.post.get_multi(db, skip=skip, limit=limit)

    async def update_post(
        self, db: AsyncSession, *, post_id: uuid.UUID, post_in: PostUpdate, user_id: uuid.UUID
    ) -> models.Post:
        post = await self.get_post(db=db, post_id=post_id)
        if post.author_id != user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await crud.post.update(db=db, db_obj=post, obj_in=post_in)

    async def delete_post(
        self, db: AsyncSession, *, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> models.Post:
        post = await self.get_post(db=db, post_id=post_id)
        if post.author_id != user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await crud.post.remove(db=db, id=post_id)

post_service = PostService()
