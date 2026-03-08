import asyncio
from database import engine, AsyncSessionLocal
from sqlalchemy import select
import models

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(models.Recorrencia).limit(5))
        rows = res.scalars().all()
        print(f"Recurrences found: {len(rows)}")
        for r in rows:
            print(f"ID: {r.id}, Desc: {r.descricao}")

if __name__ == "__main__":
    asyncio.run(check())
