from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.security import create_access_token, verify_password
from app.dependencies import get_db

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(db: Session = Depends(get_db), *, obj_in: schemas.LoginRequest):
    user = crud.user.get_by_email(db, email=obj_in.email)
    if not user or not verify_password(obj_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # The refresh token logic will be added later
    access_token = create_access_token(
        data={"identity": str(user.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": "dummy_refresh_token", # Placeholder
        "token_type": "bearer",
    }
