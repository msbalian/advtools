from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.tarefa_service import (
    get_tarefas_service,
    get_tarefa_service,
    create_tarefa_service,
    update_tarefa_service,
    delete_tarefa_service
)

router = APIRouter(prefix="/api/tarefas", tags=["Tarefas"])

@router.get("", response_model=List[schemas.TarefaResponse])
async def read_tarefas(
    processo_id: Optional[int] = Query(None),
    responsavel_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await get_tarefas_service(
        db, 
        escritorio_id=current_user.escritorio_id, 
        processo_id=processo_id, 
        responsavel_id=responsavel_id,
        cliente_id=cliente_id,
        status=status,
        limit=limit
    )

@router.post("", response_model=schemas.TarefaResponse)
async def create_tarefa(
    tarefa: schemas.TarefaCreate, 
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await create_tarefa_service(db, tarefa, escritorio_id=current_user.escritorio_id, usuario_id=current_user.id)

@router.get("/{tarefa_id}", response_model=schemas.TarefaResponse)
async def read_tarefa(
    tarefa_id: int, 
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await get_tarefa_service(db, tarefa_id, escritorio_id=current_user.escritorio_id)

@router.patch("/{tarefa_id}", response_model=schemas.TarefaResponse)
async def update_tarefa(
    tarefa_id: int, 
    tarefa: schemas.TarefaUpdate, 
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await update_tarefa_service(db, tarefa_id, tarefa, escritorio_id=current_user.escritorio_id)

@router.delete("/{tarefa_id}", status_code=204)
async def delete_tarefa(
    tarefa_id: int, 
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    await delete_tarefa_service(db, tarefa_id, escritorio_id=current_user.escritorio_id)
    return None
