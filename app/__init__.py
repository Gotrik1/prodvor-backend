
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(init_swagger=True):
    # --- ВРЕМЕННЫЙ ШАГ ДЛЯ ОТЛАДКИ ---
    # Пароль 'postgres' вставлен напрямую, так как файл .env сбрасывается.
    print("--- ИСПОЛЬЗUЮТСЯ ЖЕСТКО ЗАДАННЫЕ ЗНАЧЕНИЯ (ПАРОЛЬ 'postgres' ВКЛЮЧЕН) ---")
    
    database_url = "postgresql://postgres.ppzkctfvrxqlcrpwtuuu:postgres@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
    supabase_url = "https://ppzkctfvrxqlcrpwtuuu.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwemtjdGZ2cnhxbGNycHd0dXV1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTg5OTI3MCwiZXhwIjoyMDc3NDc1MjcwfQ.EH7NQSbnmXMRrdUrLhUy9bBlLcB7zylMHkXBIn8TqV4"
    secret_key = "a_very_secret_key"
    refresh_secret_key = "another_very_secret_key"

    os.environ['DATABASE_URL'] = database_url
    os.environ['SUPABASE_URL'] = supabase_url
    os.environ['SUPABASE_KEY'] = supabase_key
    os.environ['SECRET_KEY'] = secret_key
    os.environ['REFRESH_SECRET_KEY'] = refresh_secret_key
    # --- КОНЕЦ ВРЕМЕННОГО ШАГА ДЛЯ ОТЛАДКИ ---

    app = Flask(__name__, static_folder='../static')
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": [
                "https://6000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev/",
                "https://9000-firebase-prodvor-landin-3110-1761908712682.cluster-3gc7bglotjgwuxlqpiut7yyqt4.cloudworkstations.dev/",
                "http://localhost:3000"
                ""
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # --- JWT Configuration ---
    app.config["JWT_SECRET_KEY"] = secret_key
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    
    app.config['SECRET_KEY'] = secret_key # Legacy
    app.config['REFRESH_SECRET_KEY'] = refresh_secret_key

    # --- Flasgger (Swagger) Configuration ---
    if init_swagger:
        app.config['SWAGGER'] = {
            'title': 'Prodvor API',
            'uiversion': 3,
            "specs_route": "/apidocs/"
        }
        Swagger(app)
    # --- End Flasgger Configuration ---

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt = JWTManager(app)

    from .routes import init_routes
    init_routes(app)

    return app
