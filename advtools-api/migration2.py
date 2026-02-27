import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

engine = create_async_engine('postgresql+asyncpg://postgres:0000@localhost:5432/advtools')

async def run_migration():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN page_number INTEGER;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN x_pos FLOAT;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN y_pos FLOAT;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN width FLOAT;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN height FLOAT;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN docWidth FLOAT;"))
            await conn.execute(text("ALTER TABLE signatarios ADD COLUMN docHeight FLOAT;"))
            print("Migration successful")
        except Exception as e:
            print(f"Migration error (already exists?): {e}")

if __name__ == '__main__':
    asyncio.run(run_migration())
