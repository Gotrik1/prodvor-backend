from app.crud.base import CRUDBase
from app.models import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    pass


subscription = CRUDSubscription(Subscription)
