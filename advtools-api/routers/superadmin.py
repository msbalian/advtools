from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List

import schemas
import models
from database import get_db
from services.auth_service import get_current_superadmin

router = APIRouter(prefix="/api/admin", tags=["SuperAdmin"])

@router.get("/usuarios", response_model=List[schemas.Usuario])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    admin: models.Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(
        select(models.Usuario).options(joinedload(models.Usuario.escritorio))
    )
    return result.scalars().all()

@router.post("/usuarios/{user_id}/aprovar", response_model=schemas.Usuario)
async def approving_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: models.Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.ativo = True
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/usuarios/{user_id}/bloquear", response_model=schemas.Usuario)
async def blocking_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: models.Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode bloquear a si mesmo")
        
    user.ativo = False
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/usuarios/{user_id}", status_code=204)
async def deleting_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: models.Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir a si mesmo")
        
    await db.delete(user)
    await db.commit()
    return None
