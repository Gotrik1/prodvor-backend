import uuid
from datetime import datetime, timedelta
from typing import Any, List, Optional, Union

import jwt
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.dependencies import get_current_user, get_db, oauth2_scheme
from app.schemas.token import Msg, TokenPayload
from app.utils.token import create_access_token, create_refresh_token, ALGORITHM, verify_token
from app.utils.blacklist import add_to_blacklist

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30 # 30 days


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

    access_token = create_access_token(
        user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/logout", response_model=Msg)
async def logout(
    token: str = Depends(oauth2_scheme),
) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    add_to_blacklist(token_data.jti)
    return {"msg": "Successfully logged out"}


@router.post("/register", response_model=schemas.user.User)
async def register(
    *, 
    db: AsyncSession = Depends(get_db), 
    user_in: schemas.user.UserCreate
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
async def refresh_token(
    current_user: models.User = Depends(get_current_user),
) -> Any:
    access_token = create_access_token(
        current_user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(current_user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
