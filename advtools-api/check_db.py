import asyncio
from sqlalchemy.future import select
from database import AsyncSessionLocal
import models
import auth

async def main():
    with open('output.txt', 'w', encoding='utf-8') as f:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(models.Usuario))
            users = res.scalars().all()
            if not users:
                f.write("Nenhum usuario no banco!\n")
            for u in users:
                f.write(f"ID: {u.id}, Email: {u.email}\n")
                f.write(f"Hash: {u.senha_hash}\n")
                if auth.verify_password("123", u.senha_hash):
                    f.write(f"Senha '123' eh VALIDA para {u.email}\n")
                else:
                    f.write(f"Senha '123' eh INVALIDA para {u.email}\n")

asyncio.run(main())
