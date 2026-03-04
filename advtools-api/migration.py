import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import Config

engine = create_async_engine(Config.DATABASE_URL)

async def run_migration():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN IF NOT EXISTS arquivo_assinado_path VARCHAR(500);"))

if __name__ == '__main__':
    asyncio.run(run_migration())
