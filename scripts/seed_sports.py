
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings

# Sports data from the legacy file
sports_list = [
    {"name": "Футбол", "player_count": 11, "description": "Самый популярный спорт в мире."},
    {"name": "Баскетбол", "player_count": 5, "description": "Игра с мячом и двумя корзинами."},
    {"name": "Волейбол", "player_count": 6, "description": "Игра через сетку, где мяч не должен коснуться земли."},
    {"name": "Хоккей", "player_count": 6, "description": "Командная игра на льду с шайбой и клюшками."},
    {"name": "Теннис", "player_count": 1, "description": "Индивидуальный или парный вид спорта с ракетками и мячом."},
]

async def seed_sports():
    """
    Seeds the database with an initial list of sports.
    """
    # Use the DATABASE_URL from the environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")

    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        # Check if the sport table exists
        result = await conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sport');"))
        table_exists = result.scalar_one_or_none()

        if table_exists:
            # Truncate the table to start fresh
            await conn.execute(text("TRUNCATE TABLE sport RESTART IDENTITY CASCADE;"))
        else:
            print("Warning: 'sport' table not found. Skipping truncation.")

        # Insert new data
        for sport in sports_list:
            await conn.execute(
                text(
                    "INSERT INTO sport (name, player_count, description) VALUES (:name, :player_count, :description)"
                ),
                sport
            )

    await engine.dispose()

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(seed_sports())
    print("Successfully seeded the database with sports.")
