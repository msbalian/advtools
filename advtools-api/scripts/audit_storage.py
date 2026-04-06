import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Adicionar diretório pai ao path para importar módulos da API
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR / "advtools-api"))

# Carrega o .env da raiz
_env_path = ROOT_DIR / ".env"
load_dotenv(_env_path)

from services.storage_audit_service import run_storage_audit

if __name__ == "__main__":
    fix_mode = "--fix" in sys.argv
    print(f"Executando auditoria manual via CLI...")
    asyncio.run(run_storage_audit(fix=fix_mode))
