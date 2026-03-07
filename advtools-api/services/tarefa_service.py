from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import models
import schemas
from fastapi import HTTPException

async def create_tarefa_service(db: AsyncSession, tarefa: schemas.TarefaCreate, escritorio_id: int, usuario_id: int):
    db_tarefa = models.Tarefa(
        **tarefa.model_dump(),
        escritorio_id=escritorio_id,
        criado_por_id=usuario_id
    )
    db.add(db_tarefa)
    await db.commit()
    await db.refresh(db_tarefa)
    # Re-busca com relacionamentos carregados
    return await get_tarefa_service(db, db_tarefa.id, escritorio_id)

from typing import Optional
from sqlalchemy.orm import selectinload

async def get_tarefas_service(db: AsyncSession, escritorio_id: int, processo_id: Optional[int] = None, responsavel_id: Optional[int] = None, cliente_id: Optional[int] = None, status: Optional[str] = None, limit: Optional[int] = None):
    query = select(models.Tarefa).options(
        selectinload(models.Tarefa.responsavel),
        selectinload(models.Tarefa.cliente),
        selectinload(models.Tarefa.processo).selectinload(models.Processo.cliente)
    ).where(models.Tarefa.escritorio_id == escritorio_id)
    
    if processo_id:
        query = query.where(models.Tarefa.processo_id == processo_id)
    
    if responsavel_id:
        query = query.where(models.Tarefa.responsavel_id == responsavel_id)
        
    if status:
        query = query.where(models.Tarefa.status == status)
        
    if cliente_id:
        query = query.where(models.Tarefa.cliente_id == cliente_id)
    
    query = query.order_by(models.Tarefa.data_vencimento.asc())
    if limit:
        query = query.limit(limit)
        
    result = await db.execute(query)
    return result.scalars().all()

async def get_tarefa_service(db: AsyncSession, tarefa_id: int, escritorio_id: int):
    result = await db.execute(select(models.Tarefa).options(
        selectinload(models.Tarefa.responsavel),
        selectinload(models.Tarefa.cliente),
        selectinload(models.Tarefa.processo).selectinload(models.Processo.cliente)
    ).where(
        models.Tarefa.id == tarefa_id, 
        models.Tarefa.escritorio_id == escritorio_id
    ))
    tarefa = result.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return tarefa

async def update_tarefa_service(db: AsyncSession, tarefa_id: int, tarefa_data: schemas.TarefaUpdate, escritorio_id: int):
    db_tarefa = await get_tarefa_service(db, tarefa_id, escritorio_id)
    
    update_data = tarefa_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tarefa, key, value)
    
    await db.commit()
    await db.refresh(db_tarefa)
    return db_tarefa

async def delete_tarefa_service(db: AsyncSession, tarefa_id: int, escritorio_id: int):
    db_tarefa = await get_tarefa_service(db, tarefa_id, escritorio_id)
    await db.delete(db_tarefa)
    await db.commit()
    return True
