import os
from pathlib import Path
from dotenv import load_dotenv
import urllib.parse

# Carrega o .env da raiz do projeto (um nível acima de advtools-api)
current_dir = Path(__file__).resolve().parent
_env_path = current_dir.parent / ".env"

if not _env_path.exists():
    # Tenta no diretório atual caso o .env tenha sido movido para advtools-api/
    _env_path = current_dir / ".env"

load_dotenv(_env_path)

class Config:
    # Banco de Dados — monta a URL a partir das variáveis individuais
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "advtools-db")

    # Escapa caracteres especiais na senha e no usuário (necessário para asyncpg/SQLAlchemy)
    # Senhas com espaços ("MINHA SENHA") precisam virar "MINHA%20SENHA" na URL
    _quoted_user = urllib.parse.quote(POSTGRES_USER)
    _quoted_password = urllib.parse.quote(POSTGRES_PASSWORD)

    DATABASE_URL = (
        f"postgresql+asyncpg://{_quoted_user}:{_quoted_password}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # Chaves de API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATAJUD_KEY = os.getenv("DATAJUD_KEY")

    # PROJUDI / MNI WebService
    PROJUDI_USER = os.getenv("PROJUDI_USER")
    PROJUDI_PASSWORD = os.getenv("PROJUDI_PASSWORD")

    # CORS e Frontend
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:5173,http://localhost:5174")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Segurança e JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_padrao_mude_em_producao")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    # Prioriza APP_TIMEZONE, mas aceita o padrão TZ da VPS se existir
    APP_TIMEZONE = os.getenv("APP_TIMEZONE", os.getenv("TZ", "America/Sao_Paulo"))

    # Seed Admin
    FIRST_ADMIN_NAME = os.getenv("FIRST_ADMIN_NAME", "Super Admin")
    FIRST_ADMIN_EMAIL = os.getenv("FIRST_ADMIN_EMAIL", "admin@advtools.com.br")
    FIRST_ADMIN_PASSWORD = os.getenv("FIRST_ADMIN_PASSWORD", "123456")

    # Seed Escritório
    FIRST_OFFICE_NAME = os.getenv("FIRST_OFFICE_NAME", "ADVtools Advocacia")
    FIRST_OFFICE_DOC = os.getenv("FIRST_OFFICE_DOC", "00.000.000/0001-00")

    # Mailing
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "contato@advtools.com.br")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM = os.getenv("MAIL_FROM", "contato@advtools.com.br")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "ADVtools")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "mail.advtools.com.br")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "False").lower() in ('true', '1', 't')
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "True").lower() in ('true', '1', 't')

    @staticmethod
    def get_gemini_api_key(db_key: str = None) -> str:
        # Prioridade 1: Banco de Dados
        if db_key and db_key.strip() and len(db_key.strip()) > 10:
            key = db_key.strip()
            print(f" >>> [IA] Usando chave do BANCO (Escritório). Final: ...{key[-4:]}")
            return key
            
        # Prioridade 2: Fallback .env
        env_key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if env_key and len(env_key) > 10:
            # Filtro básico de placeholder
            if "sua_chave" not in env_key.lower():
                print(f" >>> [IA] Usando chave do .ENV. Final: ...{env_key[-4:]}")
                return env_key
            
        print(" >>> [IA] Nenhuma chave de API válida encontrada.")
        return None


