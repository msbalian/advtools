
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import AsyncSessionLocal, engine
import models
from auth import get_password_hash

async def create_root_admin():
    async with AsyncSessionLocal() as db:
        # 1. Garantir que exista ao menos um escritório para vincular o admin
        result_esc = await db.execute(select(models.Escritorio).limit(1))
        escritorio = result_esc.scalars().first()
        
        if not escritorio:
            print("Criando escritório padrão...")
            escritorio = models.Escritorio(
                nome="Escritório Admin Central",
                documento="00.000.000/0001-00"
            )
            db.add(escritorio)
            await db.commit()
            await db.refresh(escritorio)
            print(f"Escritório '{escritorio.nome}' criado com ID {escritorio.id}")

        # 2. Criar o usuário SuperAdmin
        # Verificando se já existe um admin@admin.com
        result_user = await db.execute(select(models.Usuario).filter(models.Usuario.email == "admin@admin.com"))
        user = result_user.scalars().first()
        
        if not user:
            print("Criando usuário SuperAdmin (admin@admin.com)...")
            hashed_password = get_password_hash("admin123")
            user = models.Usuario(
                email="admin@admin.com",
                senha_hash=hashed_password,
                nome="Super Administrador Root",
                escritorio_id=escritorio.id,
                tipo="Humano",
                perfil="Admin",
                is_admin=True, # PRIVILÉGIO GLOBAL
                ativo=True
            )
            db.add(user)
            await db.commit()
            print("====================================================")
            print("SUPERADMIN CRIADO COM SUCESSO!")
            print("Email: admin@admin.com")
            print("Senha: admin123")
            print("====================================================")
        else:
            print(f"O usuário {user.email} já existe.")

if __name__ == "__main__":
    asyncio.run(create_root_admin())
