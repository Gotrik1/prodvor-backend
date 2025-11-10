
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app import crud
from app.schemas.auth import LoginRequest, Token, UserRegistration
from app.schemas.user import User
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.dependencies import get_db, get_current_user, reusable_oauth2

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, operation_id="register")
def register_user(
    *, 
    db: Session = Depends(get_db), 
    user_in: UserRegistration
):
    """
    Register a new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists.",
        )
    user = crud.user.get_by_nickname(db, nickname=user_in.nickname)
    if user:
        raise HTTPException(
            status_code=409,
            detail="A user with this nickname already exists.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token, operation_id="login")
def login_for_access_token(
    request: Request, 
    db: Session = Depends(get_db), 
    form_data: LoginRequest = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud.user.get_by_email(db, email=form_data.email)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    # HACK: Временное решение для сессий, пока не выделен отдельный CRUD
    crud.user.create_session(
        db,
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/refresh", operation_id="refreshToken")
def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Refresh access token.
    """
    new_access_token = create_access_token(subject=current_user.id)
    return {"accessToken": new_access_token}

@router.post("/logout", operation_id="logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    token: str = Depends(reusable_oauth2)
):
    """
    Logout user (invalidate refresh token).
    """
    success = crud.user.delete_session(db, refresh_token=token)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Session not found or already invalidated."
        )
    return {"message": "Successfully logged out"}
