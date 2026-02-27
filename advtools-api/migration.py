import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

engine = create_async_engine('postgresql+asyncpg://postgres:0000@localhost:5432/advtools')

async def run_migration():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN IF NOT EXISTS arquivo_assinado_path VARCHAR(500);"))

if __name__ == '__main__':
    asyncio.run(run_migration())
