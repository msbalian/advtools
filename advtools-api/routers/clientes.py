from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.cliente_service import (
    get_clientes_service,
    create_cliente_service,
    get_cliente_service,
    get_servicos_by_cliente_service,
    update_cliente_service,
    delete_cliente_service
)

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("", response_model=list[schemas.Cliente])
async def read_clientes(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_clientes_service(db, escritorio_id=current_user.escritorio_id)

@router.post("", response_model=schemas.Cliente)
async def create_cliente(cliente: schemas.ClienteCreate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_cliente_service(db, cliente, escritorio_id=current_user.escritorio_id)

@router.get("/{cliente_id}", response_model=schemas.Cliente)
async def read_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_cliente_service(db, cliente_id, escritorio_id=current_user.escritorio_id)

@router.get("/{cliente_id}/servicos", response_model=list[schemas.Servico])
async def read_servicos_by_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_servicos_by_cliente_service(db, cliente_id, escritorio_id=current_user.escritorio_id)

@router.put("/{cliente_id}", response_model=schemas.Cliente)
async def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_cliente_service(db, cliente_id, cliente, escritorio_id=current_user.escritorio_id)

@router.delete("/{cliente_id}", status_code=204)
async def delete_cliente(cliente_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_cliente_service(db, cliente_id, escritorio_id=current_user.escritorio_id)
    return None
