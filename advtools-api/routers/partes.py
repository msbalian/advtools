from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.parte_service import (
    get_partes_cliente_service,
    create_parte_service,
    update_parte_service,
    delete_parte_service
)

router = APIRouter(prefix="/api/partes", tags=["Partes"])
router_clientes_partes = APIRouter(prefix="/api/clientes", tags=["Partes"])

@router_clientes_partes.get("/{cliente_id}/partes", response_model=list[schemas.ParteEnvolvida])
async def read_partes_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_partes_cliente_service(db, cliente_id, current_user.escritorio_id)

@router.post("", response_model=schemas.ParteEnvolvida)
async def create_parte(parte: schemas.ParteEnvolvidaCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_parte_service(db, parte, current_user.escritorio_id)

@router.put("/{parte_id}", response_model=schemas.ParteEnvolvida)
async def update_parte(parte_id: int, parte: schemas.ParteEnvolvidaUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_parte_service(db, parte_id, parte, current_user.escritorio_id)

@router.delete("/{parte_id}", status_code=204)
async def delete_parte(parte_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_parte_service(db, parte_id, current_user.escritorio_id)
    return None
