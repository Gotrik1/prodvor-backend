from app.crud.base import CRUDBase
from app.models.like import Like
from app.schemas.like import LikeCreate, LikeUpdate

class CRUDLike(CRUDBase[Like, LikeCreate, LikeUpdate]):
    pass

like = CRUDLike(Like)
