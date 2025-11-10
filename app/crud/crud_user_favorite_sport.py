from app.crud.base import CRUDBase
from app.models import UserFavoriteSport
from app.schemas.user_favorite_sport import UserFavoriteSportCreate, UserFavoriteSportUpdate


class CRUDUserFavoriteSport(CRUDBase[UserFavoriteSport, UserFavoriteSportCreate, UserFavoriteSportUpdate]):
    pass


user_favorite_sport = CRUDUserFavoriteSport(UserFavoriteSport)
