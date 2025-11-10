# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, Token
from app.core.security import verify_password, create_access_token

# ✔ явный импорт конкретного файла
from app.crud.user import get_by_email

router = APIRouter()

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    db_user = get_by_email(db, email=payload.email)  # <- без _crud.user
    if not db_user or not verify_password(payload.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token({"identity": str(db_user.id)})
    return {"access_token": token, "refresh_token": "", "token_type": "bearer"}
