from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.servico_service import (
    get_servicos_service,
    create_servico_service,
    update_servico_service,
    delete_servico_service
)

router = APIRouter(prefix="/api/servicos", tags=["Servicos"])

@router.get("", response_model=list[schemas.Servico])
async def read_servicos(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_servicos_service(db, escritorio_id=current_user.escritorio_id)

@router.post("", response_model=schemas.Servico)
async def create_servico(servico: schemas.ServicoCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_servico_service(db, servico, escritorio_id=current_user.escritorio_id)

@router.put("/{servico_id}", response_model=schemas.Servico)
async def update_servico(servico_id: int, servico: schemas.ServicoUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_servico_service(db, servico_id, servico, escritorio_id=current_user.escritorio_id)

@router.delete("/{servico_id}", status_code=204)
async def delete_servico(servico_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_servico_service(db, servico_id, escritorio_id=current_user.escritorio_id)
    return None
