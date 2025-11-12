from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID

class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    async def create_with_author(self, db: AsyncSession, *, obj_in: CommentCreate, author_id: UUID) -> Comment:
        db_obj = self.model(**obj_in.dict(), authorId=author_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_post(self, db: AsyncSession, *, post_id: UUID, skip: int = 0, limit: int = 100) -> list[Comment]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.postId == post_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

comment = CRUDComment(Comment)
