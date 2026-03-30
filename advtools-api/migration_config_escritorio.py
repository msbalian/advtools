import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import Config

engine = create_async_engine(Config.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def migrate():
    async with engine.begin() as conn:
        print("Iniciando migração de configurações do escritório...")
        
        # 1. Tabela pastas_trabalho
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pastas_trabalho (
                id SERIAL PRIMARY KEY,
                escritorio_id INTEGER NOT NULL REFERENCES escritorios(id),
                nome VARCHAR(255) NOT NULL
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_pastas_trabalho_escritorio ON pastas_trabalho(escritorio_id)
        """))
        
        # 2. Tabela tipos_servico
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tipos_servico (
                id SERIAL PRIMARY KEY,
                escritorio_id INTEGER NOT NULL REFERENCES escritorios(id),
                nome VARCHAR(255) NOT NULL
            )
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tipos_servico_escritorio ON tipos_servico(escritorio_id)
        """))
        
        # 3. Alterar processos para adicionar pasta_trabalho_id
        await conn.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='processos' AND COLUMN_NAME='pasta_trabalho_id') THEN
                    ALTER TABLE processos ADD COLUMN pasta_trabalho_id INTEGER REFERENCES pastas_trabalho(id);
                END IF;
            END $$;
        """))
        
        # 4. Alterar servicos para adicionar tipo_servico_id
        await conn.execute(text("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='servicos' AND COLUMN_NAME='tipo_servico_id') THEN
                    ALTER TABLE servicos ADD COLUMN tipo_servico_id INTEGER REFERENCES tipos_servico(id);
                END IF;
            END $$;
        """))
        
        print("Migração concluída com sucesso!")

if __name__ == "__main__":
    asyncio.run(migrate())
