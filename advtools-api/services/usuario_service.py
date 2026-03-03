from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
import crud

async def get_usuarios_service(db: AsyncSession, escritorio_id: int):
    return await crud.get_usuarios(db, escritorio_id=escritorio_id)

async def create_usuario_equipe_service(db: AsyncSession, current_user: models.Usuario, user_in: schemas.UsuarioCreate):
    if not (current_user.is_admin or current_user.perfil == 'Admin'):
        raise HTTPException(status_code=403, detail="Apenas administradores podem adicionar usuários.")
        
    user_in.escritorio_id = current_user.escritorio_id
    
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
        
    return await crud.create_user(db, user_in)

async def update_usuario_equipe_service(db: AsyncSession, current_user: models.Usuario, user_id: int, user_update: schemas.UsuarioUpdate):
    is_self = current_user.id == user_id
    is_office_admin = current_user.perfil == 'Admin'
    
    if not (current_user.is_admin or is_office_admin or is_self):
        raise HTTPException(status_code=403, detail="Sem permissão para editar outros usuários.")
        
    updated_user = await crud.update_usuario(db, user_id, current_user.escritorio_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return updated_user

async def delete_usuario_equipe_service(db: AsyncSession, current_user: models.Usuario, user_id: int):
    if not (current_user.is_admin or current_user.perfil == 'Admin'):
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir usuários.")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Não é possível excluir a si mesmo.")
        
    success = await crud.delete_usuario(db, user_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return success
