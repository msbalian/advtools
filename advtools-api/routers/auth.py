from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db

from services.auth_service import get_current_user, authenticate_user, register_new_user, process_forgot_password, process_reset_password

router = APIRouter(prefix="/api", tags=["Auth"])

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, form_data)

@router.post("/register", response_model=schemas.Usuario)
async def register_user(user_in: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    return await register_new_user(db, user_in)

@router.get("/me", response_model=schemas.Usuario)
async def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
async def forgot_password(req: schemas.ForgotPasswordRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    await process_forgot_password(db, background_tasks, req.email)
    return {"message": "Se o email estiver cadastrado, as instruções foram enviadas."}

@router.post("/reset-password")
async def reset_password(req: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await process_reset_password(db, req.token, req.new_password)
    return {"message": "Senha redefinida com sucesso."}
