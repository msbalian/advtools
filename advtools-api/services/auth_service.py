from fastapi import Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

import auth as auth_utils
import crud
import schemas
import models
from database import get_db
from config import Config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = await crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_superadmin(current_user: models.Usuario = Depends(get_current_user)) -> models.Usuario:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operação permitida apenas para Super Administradores"
        )
    return current_user

async def authenticate_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm):
    user = await crud.get_user_by_email(db, email=form_data.username)
    
    # Bootstrap: Se o login falhar e não houver NENHUM superadmin no banco, cria o padrão do .env
    if not user:
        if not await crud.check_any_superadmin_exists(db):
            # Cria escritório e admin root silenciosamente
            default_esc = await crud.ensure_default_office(db)
            admin_in = schemas.UsuarioCreate(
                nome=Config.FIRST_ADMIN_NAME,
                email=Config.FIRST_ADMIN_EMAIL,
                senha=Config.FIRST_ADMIN_PASSWORD,
                escritorio_id=default_esc.id,
                is_admin=True,
                perfil="Admin",
                ativo=True
            )
            await crud.create_user(db, admin_in)
            # Tenta buscar novamente o usuário (pode ser o que o usuário acabou de tentar logar se bater com o .env)
            user = await crud.get_user_by_email(db, email=form_data.username)

    if not user or not auth_utils.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_utils.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def register_new_user(db: AsyncSession, user_in: schemas.UsuarioCreate):
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
        
    user = await crud.create_user(db, user_in)
    return user

async def process_forgot_password(db: AsyncSession, background_tasks: BackgroundTasks, email: str):
    import secrets
    from datetime import datetime, timedelta, timezone
    from services.email_service import send_password_reset_email
    from utils.time_utils import get_now
    
    user = await crud.get_user_by_email(db, email=email)
    if not user or not user.ativo:
        # Por segurança, retornamos True mesmo se nao existir
        return True
        
    token = secrets.token_urlsafe(32)
    # Usa o timezone configurado no .env (centralizado no utilitário)
    expires = get_now() + timedelta(minutes=15)
    
    await crud.set_password_reset_token(db, user.id, token, expires)
    await send_password_reset_email(background_tasks, email, token)
    return True

async def process_reset_password(db: AsyncSession, token: str, new_password: str):
    user = await crud.get_user_by_reset_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
        
    nova_senha_hash = auth_utils.get_password_hash(new_password)
    await crud.update_password_and_clear_token(db, user.id, nova_senha_hash)
    return True
