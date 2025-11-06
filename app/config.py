import os

class BaseConfig:
    """Базовая конфигурация."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    # Секреты JWT
    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    SECRET_KEY = JWT_SECRET_KEY
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "change-me-in-production-2")

    # Домены для CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "https://prodvor.website",
        "https://6000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev",
        "https://9000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev",
    ]


class LocalConfig(BaseConfig):
    """Конфигурация для локальной разработки."""
    # На локалке приоритет у LOCAL_DATABASE_URL из .env.local, 
    # затем у DATABASE_URL из docker-compose или .env.
    SQLALCHEMY_DATABASE_URI = os.getenv("LOCAL_DATABASE_URL") or os.getenv("DATABASE_URL")


class ProdConfig(BaseConfig):
    """Конфигурация для продакшена."""
    # На проде строго используется DATABASE_URL из переменных окружения сервера.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL is not set for production environment!")


# Словарь для выбора конфигурации по FLASK_ENV
CONFIG_MAP = {
    'development': LocalConfig,
    'production': ProdConfig,
}
