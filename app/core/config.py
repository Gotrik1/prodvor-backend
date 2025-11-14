# app/core/config.py
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Core settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FastAPI Project"

    # Database settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    
    # SQLAlchemy
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # JWT Settings for python-jose
    # Убран небезопасный дефолт. Ключ ДОЛЖЕН быть задан в окружении.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env_file") # Оставил дефолт для тестов, но с предупреждением
    ALGORITHM: str = "HS256"
    
    # Сроки жизни токенов
    # Access-токен живет 1 час
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Refresh-токен живет 7 дней
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
