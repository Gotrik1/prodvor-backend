# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, User
from app.services.auth_service import auth_service

router = APIRouter()

@router.post("/register", response_model=User)
async def register(
    *, 
    db: AsyncSession = Depends(get_db), 
    user_in: UserCreate
) -> User:
    user = await auth_service.register_user(db, user_in=user_in)
    return user

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = await auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    user_agent = request.headers.get("user-agent", "unknown")
    ip_address = request.client.host

    access_token, refresh_token = await auth_service.create_session(
        db, user_id=user.id, user_agent=user_agent, ip_address=ip_address
    )

    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=Token)
async def refresh(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token_request: RefreshTokenRequest = Depends(),
) -> Token:
    user_agent = request.headers.get("user-agent", "unknown")
    ip_address = request.client.host

    new_access_token, new_refresh_token = await auth_service.refresh_session(
        db, refresh_token=token_request.refresh_token, user_agent=user_agent, ip_address=ip_address
    )

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}

@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db), 
    token_request: RefreshTokenRequest = Depends()
) -> Response:
    await auth_service.logout(db, refresh_token=token_request.refresh_token)
    return Response(status_code=200, content="Successfully logged out")
