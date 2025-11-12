import asyncio
from sqlalchemy import text
from app.db.session import engine

async def main():
    """
    Connects to the database, drops all tables, and properly disposes of the engine.
    """
    print("Connecting to the database to drop all tables...")
    async with engine.connect() as conn:
        try:
            await conn.begin()
            print("Dropping all tables in public schema...")
            await conn.execute(text("""
                DO $$
                DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END$$;
            """))
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            await conn.commit()
            print("All tables dropped successfully.")
        except Exception as e:
            await conn.rollback()
            print(f"An error occurred while dropping tables: {e}")
            raise

    # Dispose of the engine after all operations are complete
    print("Disposing database engine...")
    await engine.dispose()
    print("Engine disposed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Script failed with error: {e}")
        # Ensure engine is disposed even if main fails
        asyncio.run(engine.dispose())
