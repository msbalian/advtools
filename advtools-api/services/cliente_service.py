from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
import models
import crud

async def get_clientes_service(db: AsyncSession, escritorio_id: int):
    return await crud.get_clientes(db, escritorio_id=escritorio_id)

async def create_cliente_service(db: AsyncSession, cliente: schemas.ClienteCreate, escritorio_id: int):
    return await crud.create_cliente(db, cliente, escritorio_id=escritorio_id)

async def get_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    cliente = await crud.get_cliente(db, cliente_id, escritorio_id=escritorio_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

async def get_servicos_by_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    return await crud.get_servicos_by_cliente(db, cliente_id, escritorio_id=escritorio_id)

async def update_cliente_service(db: AsyncSession, cliente_id: int, cliente: schemas.ClienteUpdate, escritorio_id: int):
    updated_cliente = await crud.update_cliente(db, cliente_id, cliente, escritorio_id=escritorio_id)
    if not updated_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated_cliente

async def delete_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    success = await crud.delete_cliente(db, cliente_id, escritorio_id=escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return success
