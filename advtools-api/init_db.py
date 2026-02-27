import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, AsyncSessionLocal
import models
import schemas
import crud

async def init_default_data():
    async with AsyncSessionLocal() as db:
        print("Iniciando verificação de dados padrão...")

        # 1. Garante Escritório Padrão
        result = await db.execute(select(models.Escritorio).filter(models.Escritorio.id == 1))
        escritorio = result.scalars().first()
        
        if not escritorio:
            print("Escritório padrão não encontrado. Criando 'ADVtools Advocacia'...")
            escritorio = models.Escritorio(id=1, nome="ADVtools Advocacia", documento="00.000.000/0001-00")
            db.add(escritorio)
            await db.commit()
            print("Escritório criado com sucesso.")
        
        # 2. Garante Usuário Administrador (Fernando)
        result = await db.execute(select(models.Usuario).filter(models.Usuario.email == 'fernando@primejud.com.br'))
        admin_user = result.scalars().first()

        if not admin_user:
            print("Usuário Admin não encontrado. Criando 'fernando@primejud.com.br'...")
            user_create = schemas.UsuarioCreate(
                nome="Fernando Cozac",
                email="fernando@primejud.com.br",
                senha="123", # Senha padrão simples para o desenvolvimento local
                tipo="Humano",
                perfil="Admin",
                is_admin=True,
                ativo=True,
                escritorio_id=1
            )
            await crud.create_user(db, user_create)
            print("Usuário Admin criado com sucesso.")
        else:
            print("Escritório e Usuário Admin já estão configurados.")

async def main():
    await init_default_data()

if __name__ == "__main__":
    asyncio.run(main())
