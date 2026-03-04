import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Banco de Dados
    DATABASE_URL = os.getenv("DATABASE_URL")

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
