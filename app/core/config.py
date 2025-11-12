# app/core/config.py
from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- базовые поля ---
    PROJECT_NAME: str = "Prodvor API"
    ENV: str = "dev"

    # --- JWT-токены ---
    SECRET_KEY: str = "a_very_secret_key"  # ключ для подписи JWT
    ALGORITHM: str = "HS256"                # алгоритм подписи
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365 * 100 # 100 лет

    # --- База данных (async SQLAlchemy 2.x) ---
    DATABASE_URL: str = Field(..., description="postgresql+asyncpg://user:pass@host:port/db")

    # --- CORS ---
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # Pydantic v2: конфиг через SettingsConfigDict
    model_config = SettingsConfigDict(
        env_file=".env",       # грузим .env
        env_file_encoding="utf-8",
        extra="ignore",        # игнорим лишние переменные
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
