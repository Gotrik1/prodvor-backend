from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import user as user_crud
from app import schemas # schemas все еще нужны для валидации запроса и формата ответа
from app.core.security import create_access_token, verify_password
from app.dependencies import get_db

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(db: Session = Depends(get_db), *, obj_in: schemas.LoginRequest):
    db_user = user_crud.get_by_email(db, email=obj_in.email)

    # Важно: db_user теперь RowProxy (как dict), а не ORM-объект.
    # Обращаемся к полям по именам колонок из legacy-схемы.
    if not db_user or not verify_password(obj_in.password, db_user['password_hash']):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Передаем identity напрямую в функцию создания токена.
    # Поле id берется из отраженной таблицы.
    access_token = create_access_token(
        identity=str(db_user['id'])
    )

    return {
        "access_token": access_token,
        "refresh_token": "dummy_refresh_token", # Заглушка, как и договорились
        "token_type": "bearer",
    }
