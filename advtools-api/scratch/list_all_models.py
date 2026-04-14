import requests
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import AsyncSessionLocal
from models import Escritorio
from sqlalchemy import select

async def list_all():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Escritorio).limit(1))
        esc = result.scalars().first()
        api_key = esc.gemini_api_key.strip()
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        resp = requests.get(url)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print(f"DEBUG_MODEL_LIST_START")
            for m in models:
                name = m.get('name')
                if "gemini" in name.lower():
                    print(f"MODEL: {name}")
            print(f"DEBUG_MODEL_LIST_END")
        else:
            print(f"Erro: {resp.text}")

if __name__ == "__main__":
    asyncio.run(list_all())
