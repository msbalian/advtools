import asyncio
import os
from sqlalchemy import select
from database import AsyncSessionLocal
import models

async def populate_sizes():
    async with AsyncSessionLocal() as db:
        print("Iniciando povoamento de tamanhos...")
        
        # Documentos Cliente
        result = await db.execute(select(models.DocumentoCliente))
        docs = result.scalars().all()
        for doc in docs:
            if doc.tamanho is None or doc.tamanho == 0:
                # Tenta localizar o arquivo
                path = os.path.join("static", doc.arquivo_path)
                if not os.path.exists(path):
                    path = os.path.join("static/armazenamento", doc.arquivo_path)
                
                if os.path.exists(path) and os.path.isfile(path):
                    doc.tamanho = os.path.getsize(path)
                    print(f"Doc {doc.id}: {doc.tamanho} bytes")
        
        # Modelos
        result = await db.execute(select(models.ModeloDocumento))
        modelos = result.scalars().all()
        for mod in modelos:
            if mod.tamanho is None or mod.tamanho == 0:
                path = os.path.join("static", mod.arquivo_path)
                if not os.path.exists(path):
                    path = os.path.join("static/armazenamento", mod.arquivo_path)
                
                if os.path.exists(path) and os.path.isfile(path):
                    mod.tamanho = os.path.getsize(path)
                    print(f"Modelo {mod.id}: {mod.tamanho} bytes")
                    
        await db.commit()
    print("Concluído.")

if __name__ == "__main__":
    asyncio.run(populate_sizes())
