import asyncio
import sys
import os

# Adiciona o diretório superior ao path para encontrar database e models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal
from models import Escritorio
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Escritorio))
        escritorios = result.scalars().all()
        for esc in escritorios:
            key = (esc.gemini_api_key or "").strip()
            masked = f"...{key[-4:]}" if len(key) > 4 else "EMPTY"
            print(f"ID: {esc.id} | Nome: {esc.nome} | Key: {masked} | Len: {len(key)}")

if __name__ == "__main__":
    asyncio.run(check())
