
import os
from datetime import timedelta
from uuid import UUID
from apiflask import APIFlask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from .s3_service import S3Service

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
jwt = JWTManager()
s3_service = S3Service()

def create_app():
    """Фабрика для создания экземпляра Flask приложения."""

    app = APIFlask(
        __name__,
        title="Prodvor API",
        version="1.0"
    )

    # --- Конфигурация ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # --- Строгая конфигурация JWT ---
    app.config.update(
        JWT_TOKEN_LOCATION=['headers'],
        JWT_HEADER_NAME='Authorization',
        JWT_HEADER_TYPE='Bearer',
        PROPAGATE_EXCEPTIONS=True
    )

    # --- S3 Конфигурация ---
    app.config['S3_ENDPOINT'] = os.environ.get('S3_ENDPOINT')
    app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')
    app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')
    app.config['S3_BUCKET_NAME'] = os.environ.get('S3_BUCKET_NAME')
    app.config['S3_SECURE'] = os.environ.get('S3_SECURE', 'False').lower() in ['true', '1']

    # --- OpenAPI (Swagger) Конфигурация ---
    app.security_schemes = {
        'bearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Аутентификационный токен JWT.'
        }
    }

    # --- Инициализация расширений ---
    from . import errors
    from .models import User  # Импортируем модель User

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/v1/*": {"origins": "*"}})
    jwt.init_app(app)
    s3_service.init_app(app)
    errors.init_app(app)

    # --- Кастомизация OpenAPI Spec ---
    @app.spec_processor
    def customize_spec(spec):
        """Заменяет 'name' на 'description' в поле 'servers'."""
        spec['servers'] = [
            {
                'url': 'https://8080-firebase-prodvor-backend-1761850902881.cluster-ombtxv25tbd6yrjpp3lukp6zhc.cloudworkstations.dev',
                'description': 'Development'
            },
            {
                'url': 'https://prodvor.ru',
                'description': 'Production'
            },
            {
                'url': 'http://localhost:8080',
                'description': 'Local'
            }
        ]
        return spec

    # --- JWT error handlers (диагностика 401) ---
    @jwt.unauthorized_loader
    def _jwt_missing(msg: str):
        app.logger.error(f"JWT missing: {msg}")
        return jsonify(error="missing_token", detail=msg), 401

    @jwt.invalid_token_loader
    def _jwt_invalid(reason: str):
        app.logger.error(f"JWT invalid: {reason}")
        return jsonify(error="invalid_token", detail=reason), 401

    @jwt.expired_token_loader
    def _jwt_expired(jwt_header, jwt_payload):
        app.logger.error("JWT expired")
        return jsonify(error="expired_token"), 401

    @jwt.revoked_token_loader
    def _jwt_revoked(jwt_header, jwt_payload):
        app.logger.error("JWT revoked")
        return jsonify(error="revoked_token"), 401

    # --- Настройка загрузчика пользователя для JWT ---
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Эта функция вызывается при доступе к защищенному эндпоинту
        и должна возвращать объект, представляющий пользователя.
        """
        identity = jwt_data["sub"]
        try:
            uid = UUID(str(identity))
            return User.query.get(uid)
        except (ValueError, TypeError):
            return User.query.get(identity)

    with app.app_context():
        # --- Регистрация Blueprints ---
        from .routes import auth_bp, users_bp, uploads_bp, teams_bp, sports_bp, playgrounds_bp, tournaments_bp, posts_bp, sponsors_bp, lfg_bp

        app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
        app.register_blueprint(users_bp)
        app.register_blueprint(uploads_bp)
        app.register_blueprint(teams_bp)
        app.register_blueprint(sports_bp, url_prefix='/api/v1/sports')
        app.register_blueprint(playgrounds_bp, url_prefix='/api/v1/playgrounds')
        app.register_blueprint(tournaments_bp)
        app.register_blueprint(posts_bp, url_prefix='/api/v1/posts')
        app.register_blueprint(sponsors_bp)
        app.register_blueprint(lfg_bp, url_prefix='/api/v1')

    return app

# Создаем экземпляр для простоты запуска (flask run)
app = create_app()
