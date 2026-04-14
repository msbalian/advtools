import requests
import json
import sys
import os

# Adiciona o diretório superior ao path para encontrar database e models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import AsyncSessionLocal
from models import Escritorio
from sqlalchemy import select
import asyncio

async def test_key():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Escritorio).limit(1))
        esc = result.scalars().first()
        if not esc or not esc.gemini_api_key:
            print("Nenhuma chave no banco.")
            return
        
        api_key = esc.gemini_api_key.strip()
        versions = ["v1", "v1beta"]
        
        for v in versions:
            print(f"\n--- Testando Versão {v} ---")
            url = f"https://generativelanguage.googleapis.com/{v}/models?key={api_key}"
            try:
                resp = requests.get(url, timeout=10)
                print(f"Status: {resp.status_code}")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    for m in models[:10]: # Mostra os 10 primeiros
                        print(f" - {m.get('name')} | {m.get('displayName')}")
                else:
                    print(f"Erro: {resp.text[:200]}")
            except Exception as e:
                print(f"Excessão: {e}")

if __name__ == "__main__":
    asyncio.run(test_key())
