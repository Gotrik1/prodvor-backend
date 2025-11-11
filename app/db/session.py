# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

from app.core.config import settings

url = str(settings.DATABASE_URL)
assert "+asyncpg" in url, f"Expected asyncpg driver, got: {url}"

engine = create_async_engine(
    settings.DATABASE_URL,  # должен содержать +asyncpg
    pool_pre_ping=True,
    future=True,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
