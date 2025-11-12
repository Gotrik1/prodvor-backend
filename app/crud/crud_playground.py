from app.crud.base import CRUDBase
from app.models.playground import Playground
from app.schemas.playground import PlaygroundCreate, PlaygroundUpdate

class CRUDPlayground(CRUDBase[Playground, PlaygroundCreate, PlaygroundUpdate]):
    pass

playground = CRUDPlayground(Playground)
