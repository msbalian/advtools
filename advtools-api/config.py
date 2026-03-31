import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega o .env da raiz do projeto (um nível acima de advtools-api)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

class Config:
    # Banco de Dados — monta a URL a partir das variáveis individuais
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "advtools-db")

    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Chaves de API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATAJUD_KEY = os.getenv("DATAJUD_KEY")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:5173,http://localhost:5174")

    # Segurança e JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_padrao_mude_em_producao")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    # Seed Admin
    FIRST_ADMIN_NAME = os.getenv("FIRST_ADMIN_NAME", "Super Admin")
    FIRST_ADMIN_EMAIL = os.getenv("FIRST_ADMIN_EMAIL", "admin@advtools.com.br")
    FIRST_ADMIN_PASSWORD = os.getenv("FIRST_ADMIN_PASSWORD", "123456")

    # Seed Escritório
    FIRST_OFFICE_NAME = os.getenv("FIRST_OFFICE_NAME", "ADVtools Advocacia")
    FIRST_OFFICE_DOC = os.getenv("FIRST_OFFICE_DOC", "00.000.000/0001-00")
