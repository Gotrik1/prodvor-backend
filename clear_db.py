# clear_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from app.core.config import settings

async def main():
    """
    Connects to the database, drops the public schema, recreates it,
    and properly disposes of the engine.
    This ensures a completely clean environment.
    """
    print("Connecting to the database to wipe the public schema...")
    # Connect to the database
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        try:
            print("Dropping public schema...")
            # Use CASCADE to drop all objects within the schema
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            print("Public schema dropped.")

            print("Creating public schema...")
            await conn.execute(text("CREATE SCHEMA public"))
            print("Public schema created.")

        except Exception as e:
            print(f"An error occurred during schema wipe and recreate: {e}")
        finally:
            # It's important to close the connection in the pool
            await conn.close()

    print("Disposing database engine...")
    await engine.dispose()
    print("Engine disposed.")

if __name__ == "__main__":
    print("Wiping the public schema...")
    asyncio.run(main())
    print("Schema wipe complete.")
