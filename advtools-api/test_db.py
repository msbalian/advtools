import asyncio
from sqlalchemy import text
from database import engine

async def test_conn():
    try:
        print("Testando conexão com o banco...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Resultado: {result.scalar()}")
            print("Conexão OK!")
    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
