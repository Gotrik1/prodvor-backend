
import os
from datetime import timedelta
from apiflask import APIFlask
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
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=365)
    
    # --- S3 Конфигурация ---
    app.config['S3_ENDPOINT'] = os.environ.get('S3_ENDPOINT')
    app.config['S3_ACCESS_KEY'] = os.environ.get('S3_ACCESS_KEY')
    app.config['S3_SECRET_KEY'] = os.environ.get('S3_SECRET_KEY')
    app.config['S3_BUCKET_NAME'] = os.environ.get('S3_BUCKET_NAME')
    app.config['S3_SECURE'] = os.environ.get('S3_SECURE', 'False').lower() in ['true', '1']

    # --- OpenAPI (Swagger) Конфигурация ---
    app.config['SERVERS'] = [
        {'name': 'Development', 'url': 'http://localhost:5000'},
        {'name': 'Production', 'url': 'https://prodvor.ru'}
    ]
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
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/v1/*": {"origins": "*"}})
    jwt.init_app(app)
    s3_service.init_app(app)
    errors.init_app(app)

    with app.app_context():
        # Импортируем модели
        from . import models

        # --- Регистрация Blueprints ---
        from .routes.auth import auth_bp
        from .routes.users import users_bp
        from .routes.uploads import uploads_bp
        from .routes.teams import teams_bp
        from .routes.sports import sports_bp
        from .routes.playgrounds import playgrounds_bp
        from .routes.tournaments import tournaments_bp
        from .routes.posts import posts_bp
        from .routes.sponsors import sponsors_bp
        from .routes.lfg import lfg_bp
        
        # Регистрация Blueprints
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
