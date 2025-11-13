from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.dependencies import get_current_user, get_db, oauth2_scheme
from app.schemas.token import Msg
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login", response_model=schemas.token.Token)
async def login(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=user.id,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=Msg)
async def logout(token: str = Depends(oauth2_scheme)) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.verify_token(
            token=token, 
            secret_key=settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM, 
            credentials_exception=credentials_exception
        )
        # Add token to blacklist
        security.add_to_blacklist(payload.jti)
        return {"msg": "Successfully logged out"}
    except Exception:
        raise credentials_exception


@router.post("/register", response_model=schemas.user.User)
async def register(
    *, db: AsyncSession = Depends(get_db), user_in: schemas.user.UserCreate
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.post("/refresh", response_model=schemas.token.Token)
async def refresh_token(current_user: models.User = Depends(get_current_user)) -> Any:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=current_user.id, 
        secret_key=settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM,
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=current_user.id, 
        secret_key=settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM,
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
