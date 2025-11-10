
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, Token
from app.core.security import verify_password, create_access_token
from app import crud as _crud

router = APIRouter()

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # не называем переменную 'user', чтобы не тень CRUДа
    u = _crud.user.get_by_email(db, email=payload.email)
    if not u:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password")

    # имя поля как в твоей БД (во Flask было password_hash)
    hashed = u.get("password_hash")
    if not hashed or not verify_password(payload.password, hashed):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password")

    # payload как во Flask-JWT-Extended: identity → sub
    access_token = create_access_token({"identity": str(u["id"]), "sub": str(u["id"])})
    # refresh позже; сейчас заглушка
    return {"access_token": access_token, "refresh_token": "", "token_type": "bearer"}
