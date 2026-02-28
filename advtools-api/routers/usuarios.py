from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.usuario_service import (
    get_usuarios_service,
    create_usuario_equipe_service,
    update_usuario_equipe_service,
    delete_usuario_equipe_service
)

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

@router.get("", response_model=list[schemas.Usuario])
async def read_usuarios(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_usuarios_service(db, current_user.escritorio_id)

@router.post("", response_model=schemas.Usuario)
async def create_usuario_equipe(user_in: schemas.UsuarioCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_usuario_equipe_service(db, current_user, user_in)

@router.put("/{user_id}", response_model=schemas.Usuario)
async def update_usuario_equipe(user_id: int, user_update: schemas.UsuarioUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_usuario_equipe_service(db, current_user, user_id, user_update)

@router.delete("/{user_id}", status_code=204)
async def delete_usuario_equipe(user_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await delete_usuario_equipe_service(db, current_user, user_id)
