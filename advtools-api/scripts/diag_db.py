import asyncio
import os
import asyncpg
from dotenv import load_dotenv
from pathlib import Path

# Carrega o .env da raiz (3 níveis acima de scripts/)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
print(f"DEBUG: Tentando carregar .env de: {_env_path}")
load_dotenv(_env_path)

async def check():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "advtools-db")
    
    print(f"DEBUG: Conectando em {user}@{host}:{port}/{database} com senha {password}")
    
    try:
        conn = await asyncpg.connect(user=user, password=password, database=database, host=host, port=port)
        res = await conn.fetch("SELECT count(*) FROM usuarios")
        print(f"RESULT: Usuarios count = {res[0][0]}")
        res_mods = await conn.fetch("SELECT count(*) FROM modelos_documento")
        print(f"RESULT: Modelos count = {res_mods[0][0]}")
        await conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check())
