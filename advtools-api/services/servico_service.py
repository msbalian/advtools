from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import schemas
import models
import crud

async def get_servicos_service(db: AsyncSession, escritorio_id: int):
    return await crud.get_servicos(db, escritorio_id=escritorio_id)

async def create_servico_service(db: AsyncSession, servico: schemas.ServicoCreate, escritorio_id: int):
    return await crud.create_servico(db, servico, escritorio_id=escritorio_id)

async def update_servico_service(db: AsyncSession, servico_id: int, servico: schemas.ServicoUpdate, escritorio_id: int):
    updated_servico = await crud.update_servico(db, servico_id, servico, escritorio_id=escritorio_id)
    if not updated_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return updated_servico

async def delete_servico_service(db: AsyncSession, servico_id: int, escritorio_id: int):
    success = await crud.delete_servico(db, servico_id, escritorio_id=escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return success
