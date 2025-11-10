from sqlalchemy.orm import Session
from app.models import User

def get_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()
