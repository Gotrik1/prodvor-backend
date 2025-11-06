import os

class BaseConfig:
    """Базовая конфигурация."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 20,
    }
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY", JWT_SECRET_KEY)
    CORS_ORIGINS = [
        "http://localhost:3000",
        "https://prodvor.website",
        "https://6000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev",
        "https://9000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev",
    ]
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    @staticmethod
    def init_app(app):
        pass # Базовый класс ничего не делает

class LocalConfig(BaseConfig):
    """Конфигурация для локальной разработки."""
    SQLALCHEMY_DATABASE_URI = os.getenv("LOCAL_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        if not app.config.get('SQLALCHEMY_DATABASE_URI'): 
            print("Предупреждение: Не задана DATABASE_URL...")
        if not app.config.get('JWT_SECRET_KEY'):
            print("Предупреждение: JWT_SECRET_KEY не установлен... Используется ключ по умолчанию.")
            app.config['JWT_SECRET_KEY'] = "unsafe-default-dev-key"
            app.config['SECRET_KEY'] = "unsafe-default-dev-key"

class ProdConfig(BaseConfig):
    """Конфигурация для продакшена. Падает, если нет переменных."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        if not app.config.get('SQLALCHEMY_DATABASE_URI'): 
            raise ValueError("Ошибка: DATABASE_URL не установлена!")
        if not app.config.get('JWT_SECRET_KEY'): 
            raise ValueError("Ошибка: JWT_SECRET_KEY не установлена!")
        s3_vars = ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME']
        if not all(app.config.get(key) for key in s3_vars):
            raise ValueError("Ошибка: Не все переменные S3 (ENDPOINT_URL, ACCESS_KEY, SECRET_KEY, BUCKET_NAME) установлены для прода!")

CONFIG_MAP = {
    'development': LocalConfig,
    'production': ProdConfig,
}
