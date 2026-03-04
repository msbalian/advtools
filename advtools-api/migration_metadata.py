import asyncio
import os
from sqlalchemy import text
from database import engine

async def migrate():
    async with engine.begin() as conn:
        print("Iniciando migração de metadados...")
        
        # Adiciona colunas para documentos_cliente
        try:
            await conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN IF NOT EXISTS tamanho INTEGER"))
            await conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN IF NOT EXISTS data_alteracao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            print("Colunas adicionadas a documentos_cliente")
        except Exception as e:
            print(f"Erro em documentos_cliente: {e}")

        # Adiciona colunas para modelos_documento
        try:
            await conn.execute(text("ALTER TABLE modelos_documento ADD COLUMN IF NOT EXISTS tamanho INTEGER"))
            await conn.execute(text("ALTER TABLE modelos_documento ADD COLUMN IF NOT EXISTS data_alteracao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
            print("Colunas adicionadas a modelos_documento")
        except Exception as e:
            print(f"Erro em modelos_documento: {e}")
            
    print("Migração concluída.")

if __name__ == "__main__":
    asyncio.run(migrate())
