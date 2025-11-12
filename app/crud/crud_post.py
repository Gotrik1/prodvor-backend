from app.crud.base import CRUDBase
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from uuid import UUID

class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    async def create_with_author(self, db: AsyncSession, *, obj_in: PostCreate, author_id: UUID) -> Post:
        db_obj = self.model(**obj_in.dict(), author_id=author_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

post = CRUDPost(Post)
