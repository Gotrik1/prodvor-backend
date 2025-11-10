# app/models/user.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.base_class import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(120), unique=True, index=True, nullable=False)
    # ✔ Добавляем недостающие поля со скриншота
    nickname = Column(String(80), unique=True, index=True)
    firstName = Column(String(100))
    lastName = Column(String(100))
    
    # ✔ Исправляем имя колонки для пароля
    password_hash = Column(String(255), nullable=False)

    # Поле is_active удалено, т.к. его нет в реальной таблице

    # ✔ Добавляем поля s3_path и uploaded_at
    s3_path = Column(String, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
