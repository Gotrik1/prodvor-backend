from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models import Like, Post
from app.schemas.like import LikeCreate, LikeUpdate
from fastapi.encoders import jsonable_encoder
import uuid


class CRUDLike(CRUDBase[Like, LikeCreate, LikeUpdate]):
    async def create_with_user_and_post(self, db: AsyncSession, *, obj_in: LikeCreate, user_id: uuid.UUID, post_id: uuid.UUID) -> Like:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, user_id=user_id, post_id=post_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user_and_post(self, db: AsyncSession, *, user_id: uuid.UUID, post_id: uuid.UUID) -> Like | None:
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id, self.model.post_id == post_id))
        return result.scalars().first()

    async def get_like_count_for_post(self, db: AsyncSession, *, post_id: uuid.UUID) -> int:
        result = await db.execute(select(self.model).filter(self.model.post_id == post_id))
        return len(result.scalars().all())

    async def get_liked_posts_by_user(self, db: AsyncSession, *, user_id: uuid.UUID) -> list[Post]:
        result = await db.execute(
            select(Post)
            .join(Like, Post.id == Like.post_id)
            .filter(Like.user_id == user_id)
        )
        return result.scalars().all()


like = CRUDLike(Like)
