
import os
import uuid
import logging
from flask import Flask, jsonify, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

# --- Загрузка конфигурации ---
load_dotenv()
load_dotenv(dotenv_path='.env.local')
from app.config import CONFIG_MAP

# --- Инициализация Sentry (как можно раньше) ---
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(dsn=sentry_dsn, integrations=[FlaskIntegration()], traces_sample_rate=0.1, send_default_pii=True)

# --- Инициализация расширений ---
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute", "50 per second"])

def create_app(init_swagger=True):
    env = os.getenv('FLASK_ENV', 'development')
    config = CONFIG_MAP.get(env)

    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config)
    
    # --- Валидация и дополнительная настройка конфигурации ---
    config.init_app(app)

    # --- Применение расширений ---
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)
    metrics = PrometheusMetrics(app)

    cors_origins = "https://prodvor.website" if env == 'production' else app.config['CORS_ORIGINS']
    CORS(app, supports_credentials=True, resources={ r"/api/v1/*": { "origins": cors_origins } })

    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 900 # 15 минут
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000 # 30 дней
    jwt = JWTManager(app)

    # --- Middleware и обработчики ошибок ---
    @app.before_request
    def before_request_middleware():
        g.request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        sentry_sdk.set_user({"id": g.get('user_id'), "ip_address": request.remote_addr})

    @app.after_request
    def after_request_middleware(response):
        response.headers["X-Request-ID"] = g.get("request_id")
        return response

    @app.errorhandler(Exception)
    def handle_uncaught_exception(e):
        app.logger.error(f"Unhandled exception caught: {e}", exc_info=True)
        return jsonify({"error": "internal_server_error", "message": "..."}), 500

    from .models import User
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        try: user_id = int(identity)
        except (TypeError, ValueError): return None
        return User.query.get(user_id)

    # Health Checks
    @app.route("/__health")
    def health_check(): return jsonify({"status": "ok"}), 200

    @app.route("/__ready")
    def readiness_check():
        # ... (проверка БД)
        return jsonify({"status": "ok"}), 200

    # --- Регистрация Blueprints ---
    from .routes import auth_bp, sessions_bp, uploads_bp, teams_bp # <<< ИСПРАВЛЕНИЕ

    limiter.limit("10 per minute")(auth_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(sessions_bp, url_prefix='/api/v1')
    app.register_blueprint(uploads_bp, url_prefix='/api/v1')
    app.register_blueprint(teams_bp, url_prefix='/api/v1') # <<< ДОБАВЛЕНО

    if init_swagger:
        Swagger(app, config={'title': 'Prodvor API', 'uiversion': 3, "specs_route": "/apidocs/"})

    return app
