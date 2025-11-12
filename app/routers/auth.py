from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas, crud, models
from app.dependencies import get_db, get_current_user, get_current_user_from_refresh_token
from app.utils.security import add_to_blacklist
from app.core.config import settings
from app.utils.token import generate_access_token, generate_refresh_token
from jose import jwt

router = APIRouter()

@router.post("/register", response_model=schemas.user.User)
async def register(
    *, 
    db: AsyncSession = Depends(get_db), 
    user_in: schemas.user.UserCreate
):
    """
    Register a new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    return user

@router.post("/login", response_model=schemas.auth.Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": generate_access_token(
            data={"sub": str(user.id)}
        ),
        "refresh_token": generate_refresh_token(
            data={"sub": str(user.id)}
        ),
        "token_type": "bearer",
    }

@router.post("/refresh", response_model=schemas.auth.Token)
def refresh(
    current_user: models.User = Depends(get_current_user_from_refresh_token),
):
    """
    Refresh access token
    """
    return {
        "access_token": generate_access_token(
            data={"sub": str(current_user.id)}
        ),
        "refresh_token": generate_refresh_token(
            data={"sub": str(current_user.id)}
        ),
        "token_type": "bearer",
    }

@router.post("/logout", response_model=schemas.auth.Msg)
def logout(
    authorization: str = Header(...),
):
    """
    Logout user
    """
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        jti = payload.get("jti")
        if jti:
            add_to_blacklist(jti)
    except (jwt.JWTError, IndexError):
        # Ignore errors here, if the token is invalid, it's already unusable
        pass
    return {"message": "Logout successful"}
