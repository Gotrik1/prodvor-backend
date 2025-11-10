# app/routers/users.py
from fastapi import APIRouter, Depends

# ✔ Импортируем новую зависимость и схему
from app.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.get("/me", response_model=User)
def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Возвращает данные о текущем аутентифицированном пользователе.
    """
    # FastAPI автоматически преобразует dict в схему `User`
    return current_user
