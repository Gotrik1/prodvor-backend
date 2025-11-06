
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from dotenv import load_dotenv

# Загружаем переменные из .env и .env.local (если есть)
load_dotenv()
load_dotenv(dotenv_path='.env.local')

from app.config import CONFIG_MAP

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(init_swagger=True):
    env = os.getenv('FLASK_ENV', 'development')
    config = CONFIG_MAP.get(env, 'development')

    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config)

    # Настраиваем CORS на основе конфигурации
    CORS(app, supports_credentials=True, resources={
        r"/api/v1/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })

    # Настройки JWT (уже загружены из config)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    # Настройки Swagger (если нужно)
    if init_swagger:
        app.config['SWAGGER'] = {
            'title': 'Prodvor API',
            'uiversion': 3,
            "specs_route": "/apidocs/"
        }
        Swagger(app)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt = JWTManager(app)

    # Регистрация маршрутов
    from .routes import init_routes
    init_routes(app)

    return app
