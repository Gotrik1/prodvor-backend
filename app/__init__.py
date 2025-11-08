
import os
from datetime import timedelta
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flasgger import Swagger

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
jwt = JWTManager()

def create_app(init_swagger=True):
    """Фабрика для создания экземпляра Flask приложения."""
    app = Flask(__name__)

    # --- Конфигурация ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')

    # --- Настройка времени жизни токенов ---
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False # Токен обновления будет действовать до явного выхода

    # Добавляем конфигурацию для S3, чтобы она была доступна в приложении
    app.config['S3_ENDPOINT_URL'] = os.environ.get('S3_ENDPOINT_URL')
    app.config['S3_ACCESS_KEY_ID'] = os.environ.get('S3_ACCESS_KEY_ID')
    app.config['S3_SECRET_ACCESS_KEY'] = os.environ.get('S3_SECRET_ACCESS_KEY')
    app.config['S3_BUCKET_NAME'] = os.environ.get('S3_BUCKET_NAME')

    # --- Конфигурация Swagger ---
    app.config['SWAGGER'] = {
        'title': 'Prodvor API',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'swagger_ui_config': {
            'urls': [
                {
                    'url': '/static/swagger.json',
                    'name': 'API'
                }
            ]
        }
    }
    if init_swagger:
        Swagger(app)

    @app.route('/')
    def index():
        return redirect('/apidocs/')

    # --- Инициализация расширений в приложении ---
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/v1/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}}, supports_credentials=True)
    jwt.init_app(app)

    with app.app_context():
        # Импортируем модели, чтобы они были известны SQLAlchemy
        from . import models

        # --- Регистрация ВСЕХ Blueprints ---
        from .routes.auth import auth_bp
        from .routes.users import users_bp
        from .routes.teams import teams_bp
        from .routes.sessions import sessions_bp
        from .routes.legacy import legacy_bp
        from .routes.general import general_bp
        from .routes.sports import sports_bp
        from .routes.uploads import uploads_bp
        from .routes.playgrounds import playgrounds_bp
        from .routes.tournaments import tournaments_bp
        from .routes.posts import posts_bp

        # Обратите внимание, что uploads_bp уже имеет префикс, поэтому его не нужно добавлять здесь
        app.register_blueprint(uploads_bp)

        # Для остальных префикс сохраняется
        url_prefix = '/api/v1'
        app.register_blueprint(auth_bp, url_prefix=url_prefix)
        app.register_blueprint(users_bp, url_prefix=url_prefix)
        app.register_blueprint(teams_bp, url_prefix=url_prefix)
        app.register_blueprint(sessions_bp, url_prefix=url_prefix)
        app.register_blueprint(legacy_bp, url_prefix=url_prefix)
        app.register_blueprint(general_bp, url_prefix=url_prefix)
        app.register_blueprint(sports_bp, url_prefix=url_prefix)
        app.register_blueprint(playgrounds_bp, url_prefix=url_prefix)
        app.register_blueprint(tournaments_bp, url_prefix=url_prefix)
        app.register_blueprint(posts_bp, url_prefix=url_prefix)


    return app
