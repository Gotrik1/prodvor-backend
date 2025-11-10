
from sqlalchemy.orm import Session
import uuid

# HACK: При миграции используем старые модели, чтобы сохранить полную совместимость
# Позже они будут переписаны на новый стиль SQLAlchemy 2.0
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, UserSession

from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def get_by_email(db: Session, email: str) -> User | None:
    """Находит пользователя по email."""
    return db.query(User).filter(User.email == email).first()

def get_by_nickname(db: Session, nickname: str) -> User | None:
    """Находит пользователя по никнейму."""
    return db.query(User).filter(User.nickname == nickname).first()

def create(db: Session, *, obj_in: UserCreate) -> User:
    """Создает нового пользователя."""
    
    # Создаем объект пользователя, хэшируя пароль
    db_obj = User(
        id=uuid.uuid4(),
        email=obj_in.email,
        nickname=obj_in.nickname,
        password_hash=get_password_hash(obj_in.password),
        role=obj_in.role,
        city=obj_in.city,
        firstName=obj_in.firstName,
        lastName=obj_in.lastName,
        age=obj_in.age,
        gender=obj_in.gender
    )

    # В зависимости от роли, создаем соответствующий профиль
    if obj_in.role == 'player':
        db_obj.player_profile = PlayerProfile()
    elif obj_in.role == 'referee':
        db_obj.referee_profile = RefereeProfile()
    elif obj_in.role == 'coach':
        db_obj.coach_profile = CoachProfile()

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# HACK: Это временная функция для создания сессии, пока мы не перенесли эту логику
# в отдельный CRUD-модуль для сессий.
def create_session(db: Session, *, user_id: uuid.UUID, refresh_token: str, user_agent: str, ip_address: str) -> UserSession:
    """Создает запись о сессии пользователя."""
    session = UserSession(
        userId=user_id,
        refreshToken=refresh_token,
        userAgent=user_agent,
        ipAddress=ip_address
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session_by_token(db: Session, refresh_token: str) -> UserSession | None:
    return db.query(UserSession).filter(UserSession.refreshToken == refresh_token).first()

def delete_session(db: Session, refresh_token: str) -> bool:
    """Удаляет сессию пользователя по refresh token."""
    session = get_session_by_token(db, refresh_token)
    if session:
        db.delete(session)
        db.commit()
        return True
    return False
