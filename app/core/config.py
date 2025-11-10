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

    # JWT-токены
    JWT_SECRET_KEY: str = Field(alias="SECRET_KEY")
    # ✔ Добавляем псевдоним для JWT_REFRESH_SECRET_KEY
    JWT_REFRESH_SECRET_KEY: str = Field(alias="JWT_SECRET_KEY")

    # ✔ Меняем время жизни access-токена на 24 часа (1440 минут)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # ✔ Refresh-токен теперь бессрочный, это поле больше не используется для него
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30 
    ALGORITHM: str = "HS256"
    
    # Настройки CORS
    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()
