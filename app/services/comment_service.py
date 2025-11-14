
import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    async def create_comment(
        self, db: AsyncSession, *, author_id: uuid.UUID, comment_in: CommentCreate
    ) -> models.Comment:
        post = await crud.post.get(db, id=comment_in.postId)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return await crud.comment.create_with_author(
            db=db, obj_in=comment_in, author_id=author_id
        )

    async def get_comment(
        self, db: AsyncSession, *, comment_id: uuid.UUID
    ) -> models.Comment:
        comment = await crud.comment.get(db=db, id=comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        return comment

    async def get_comments_for_post(
        self, db: AsyncSession, *, post_id: uuid.UUID, skip: int, limit: int
    ) -> List[models.Comment]:
        post = await crud.post.get(db, id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return await crud.comment.get_multi_by_post(
            db, post_id=post_id, skip=skip, limit=limit
        )

    async def update_comment(
        self, db: AsyncSession, *, comment_id: uuid.UUID, comment_in: CommentUpdate, user_id: uuid.UUID
    ) -> models.Comment:
        comment = await self.get_comment(db=db, comment_id=comment_id)
        if comment.authorId != user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await crud.comment.update(db=db, db_obj=comment, obj_in=comment_in)

    async def delete_comment(
        self, db: AsyncSession, *, comment_id: uuid.UUID, user_id: uuid.UUID
    ) -> models.Comment:
        comment = await self.get_comment(db=db, comment_id=comment_id)
        if comment.authorId != user_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return await crud.comment.remove(db=db, id=comment_id)


comment_service = CommentService()
