# app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Модель конфигурации
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True, 
        extra='ignore' # Игнорировать лишние переменные
    )

    # ✔ Возвращаем PROJECT_NAME
    PROJECT_NAME: str = "Prodvor API"

    # База данных
    DATABASE_URL: str = "postgresql://user:password@localhost/db"

    # JWT-токены
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30 
    ALGORITHM: str = "HS256"
    
    # Настройки CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Redis
    REDIS_URL: str = "redis://localhost"

settings = Settings()
