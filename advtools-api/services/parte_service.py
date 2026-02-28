from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
import models
import crud

async def get_partes_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    return await crud.get_partes_cliente(db, cliente_id, escritorio_id=escritorio_id)

async def create_parte_service(db: AsyncSession, parte: schemas.ParteEnvolvidaCreate, escritorio_id: int):
    parte.escritorio_id = escritorio_id
    return await crud.create_parte_envolvida(db, parte)

async def update_parte_service(db: AsyncSession, parte_id: int, parte: schemas.ParteEnvolvidaUpdate, escritorio_id: int):
    updated_parte = await crud.update_parte_envolvida(db, parte_id, escritorio_id, parte)
    if not updated_parte:
        raise HTTPException(status_code=404, detail="Parte não encontrada")
    return updated_parte

async def delete_parte_service(db: AsyncSession, parte_id: int, escritorio_id: int):
    success = await crud.delete_parte_envolvida(db, parte_id, escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parte não encontrada")
    return success
