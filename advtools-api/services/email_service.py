from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from pathlib import Path

from config import Config

# Diretório raiz para templates
BASE_DIR = Path(__file__).resolve().parent.parent

conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=Config.MAIL_PORT,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_FROM_NAME=Config.MAIL_FROM_NAME,
    MAIL_STARTTLS=Config.MAIL_STARTTLS,
    MAIL_SSL_TLS=Config.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(BASE_DIR, 'static', 'templates')
)

fm = FastMail(conf)

async def send_password_reset_email(background_tasks: BackgroundTasks, email_to: str, reset_token: str):
    """
    Despacha o envio de email de recuperação de senha em background.
    """
    # Link do Frontend que será montado a partir da env
    frontend_url = Config.FRONTEND_URL.rstrip('/')
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    # fastapi_mail preenche as variáveis Jinja2 do HTML no dict body
    message = MessageSchema(
        subject="Recuperação de Senha - AdvTools",
        recipients=[email_to],
        template_body={"reset_link": reset_link},
        subtype=MessageType.html
    )

    # Adiciona na task do background sem travar o endpoint
    background_tasks.add_task(fm.send_message, message, template_name="reset_password.html")
    return True
