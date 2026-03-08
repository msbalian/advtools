import asyncio
from database import engine, AsyncSessionLocal
from sqlalchemy import select
import models
import json

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(models.Transacao).where(models.Transacao.recorrencia_id != None).limit(5))
        rows = res.scalars().all()
        print(f"Recurring transactions found: {len(rows)}")
        for r in rows:
            print(f"ID: {r.id}, RecID: {r.recorrencia_id}")

if __name__ == "__main__":
    asyncio.run(check())
