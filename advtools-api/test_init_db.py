import asyncio
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, AsyncSessionLocal
import models
import schemas
import crud

async def init_default_data():
    try:
        async with AsyncSessionLocal() as db:
            print("Iniciando verificação de dados padrão...")

            result = await db.execute(select(models.Escritorio).filter(models.Escritorio.id == 1))
            escritorio = result.scalars().first()
            
            if not escritorio:
                print("Escritório padrão não encontrado. Criando 'ADVtools Advocacia'...")
                escritorio = models.Escritorio(id=1, nome="ADVtools Advocacia", documento="00.000.000/0001-00")
                db.add(escritorio)
                await db.commit()
                print("Escritório criado com sucesso.")
            
            result = await db.execute(select(models.Usuario).filter(models.Usuario.email == 'fernando@primejud.com.br'))
            admin_user = result.scalars().first()

            if not admin_user:
                print("Usuário Admin não encontrado. Criando 'fernando@primejud.com.br'...")
                user_create = schemas.UsuarioCreate(
                    nome="Fernando Cozac",
                    email="fernando@primejud.com.br",
                    senha="123",
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
    except Exception as e:
        print("ERRO NO INIT_DB:")
        traceback.print_exc()

async def main():
    with open('init_db_debug.txt', 'w', encoding='utf-8') as f:
        import sys
        sys.stdout = f
        sys.stderr = f
        await init_default_data()

if __name__ == "__main__":
    asyncio.run(main())
