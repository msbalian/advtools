import os
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import engine, AsyncSessionLocal
import models
import schemas
import crud
from config import Config

async def ensure_database_exists():
    """Garante que a base de dados alvo exista, conectando-se ao banco 'postgres' padrão."""
    try:
        # Tenta conectar ao banco de sistema 'postgres'
        conn = await asyncpg.connect(
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
            database="postgres"
        )
        try:
            # Verifica se a base de dados alvo já existe
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", 
                Config.POSTGRES_DB
            )
            
            if not exists:
                print(f"Base de dados '{Config.POSTGRES_DB}' não encontrada. Criando...")
                # CREATE DATABASE não pode ser executado em uma transação.
                # asyncpg.connect() não inicia transação automática para este comando.
                await conn.execute(f'CREATE DATABASE "{Config.POSTGRES_DB}"')
                print(f"✅ Base de dados '{Config.POSTGRES_DB}' criada com sucesso.")
            else:
                print(f"ℹ️ Base de dados '{Config.POSTGRES_DB}' já existe.")
        finally:
            await conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao verificar/criar base de dados '{Config.POSTGRES_DB}': {e}")
        # Não trava o processo aqui, pois a aplicação tentará conectar normalmente depois

async def init_default_data():
    # 0. Garante que a Database existe
    await ensure_database_exists()

    admin_name = Config.FIRST_ADMIN_NAME
    admin_email = Config.FIRST_ADMIN_EMAIL
    admin_password = Config.FIRST_ADMIN_PASSWORD
    
    async with AsyncSessionLocal() as db:
        print(f"Iniciando verificação de dados padrão...")

        # 1. Garante Escritório Padrão (ID 1)
        result = await db.execute(select(models.Escritorio).filter(models.Escritorio.id == 1))
        escritorio = result.scalars().first()
        
        if not escritorio:
            print(f"Escritório padrão id=1 não encontrado. Criando '{Config.FIRST_OFFICE_NAME}'...")
            escritorio = models.Escritorio(
                id=1, 
                nome=Config.FIRST_OFFICE_NAME, 
                documento=Config.FIRST_OFFICE_DOC
            )
            db.add(escritorio)
            await db.commit()
            print("✅ Escritório padrão criado.")
        else:
            print("ℹ️ Escritório padrão já existe.")
        
        # 2. Garante Usuário Super Administrador
        result = await db.execute(select(models.Usuario).filter(models.Usuario.email == admin_email))
        admin_user = result.scalars().first()

        if not admin_user:
            print(f"Usuário Admin '{admin_email}' não encontrado. Criando...")
            user_create = schemas.UsuarioCreate(
                nome=admin_name,
                email=admin_email,
                senha=admin_password,
                tipo="Humano",
                perfil="Admin",
                is_admin=True,
                ativo=True,
                escritorio_id=1
            )
            await crud.create_user(db, user_create)
            print(f"✅ Usuário '{admin_email}' criado com sucesso.")
        else:
            print(f"ℹ️ Usuário '{admin_email}' já existe. Verificando se é admin...")
            if not admin_user.is_admin or not admin_user.ativo:
                admin_user.is_admin = True
                admin_user.ativo = True
                await db.commit()
                print(f"✅ Permissões do usuário '{admin_email}' atualizadas para Admin Ativo.")
            else:
                print(f"ℹ️ Usuário '{admin_email}' já está configurado como Admin Ativo.")

async def main():
    await init_default_data()

if __name__ == "__main__":
    asyncio.run(main())
