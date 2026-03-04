from sqlalchemy.ext.asyncio import create_async_engine
from models import Base
from config import Config
import asyncio

async_engine = create_async_engine(Config.DATABASE_URL)

async def create_tables():
    print("Creating new tables...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(create_tables())
