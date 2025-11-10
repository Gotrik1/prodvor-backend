from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Prodvor API"
    # один источник правды — как во Flask:
    DATABASE_URL: str  # в .env: DATABASE_URL=postgresql://user:pass@host:5432/db
    # JWT
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    class Config:
        env_file = ".env"

settings = Settings()
