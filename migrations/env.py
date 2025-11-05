import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# -------------------------------------------------------
# 1. Безопасная загрузка .env.local и .env
# -------------------------------------------------------
try:
    from dotenv import load_dotenv

    # пробуем загрузить .env.local (если существует)
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        print("✅ Loaded .env.local")

    # пробуем загрузить обычный .env (если есть)
    if os.path.exists(".env"):
        load_dotenv(".env")
        print("✅ Loaded .env")
except Exception as e:
    print(f"⚠️ Could not load dotenv files: {e}")

# -------------------------------------------------------
# 2. Настройка Alembic
# -------------------------------------------------------
config = context.config

# Настройка логирования Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------
# 3. Импорт приложения и метаданных
# -------------------------------------------------------
from app import create_app, db

app = create_app()
with app.app_context():
    target_metadata = db.metadata

    # ---------------------------------------------------
    # 4. Миграции
    # ---------------------------------------------------
    def run_migrations_offline() -> None:
        """Run migrations in 'offline' mode'."""
        # Берём URL из env или конфигурации приложения
        url = (
            os.getenv("DATABASE_URL")
            or config.get_main_option("sqlalchemy.database.uri")
            or app.config.get("SQLALCHEMY_DATABASE_URI")
        )

        print(f"🚀 Running offline migrations using DB URL: {url or '❌ Not found'}")

        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


    def run_migrations_online() -> None:
        """Run migrations in 'online' mode."""
        configuration = config.get_section(config.config_ini_section, {}) or {}

        # Приоритет: DATABASE_URL → SQLALCHEMY_DATABASE_URI → alembic.ini
        db_url = (
            os.getenv("DATABASE_URL")
            or app.config.get("SQLALCHEMY_DATABASE_URI")
            or config.get_main_option("sqlalchemy.database.uri")
        )

        print(f"🚀 Running online migrations using DB URL: {db_url or '❌ Not found'}")

        if db_url:
            configuration["sqlalchemy.url"] = db_url

        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()


    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
