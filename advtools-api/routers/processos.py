from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.processo_service import (
    get_processos_service,
    get_processos_by_cliente_service,
    get_processo_service,
    create_processo_service,
    update_processo_service,
    delete_processo_service,
    buscar_e_criar_datajud_service,
    atualizar_processo_datajud_service
)

router = APIRouter(prefix="/api/processos", tags=["Processos"])

@router.get("", response_model=List[schemas.ProcessoResponse])
async def read_processos(
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_processos_service(db, current_user.escritorio_id)

@router.get("/cliente/{cliente_id}", response_model=List[schemas.ProcessoResponse])
async def read_processos_by_cliente(
    cliente_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_processos_by_cliente_service(db, cliente_id, current_user.escritorio_id)

@router.post("", response_model=schemas.ProcessoResponse)
async def create_processo(
    processo: schemas.ProcessoCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_processo_service(db, processo, current_user.escritorio_id)

@router.post("/buscar-datajud", response_model=schemas.ProcessoResponse)
async def import_processo_datajud(
    request: schemas.DataJudBuscaRequest,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await buscar_e_criar_datajud_service(
        db, request, current_user.escritorio_id, current_user.id
    )

@router.get("/{processo_id}", response_model=schemas.ProcessoResponse)
async def read_processo(
    processo_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_processo_service(db, processo_id, current_user.escritorio_id)

@router.patch("/{processo_id}", response_model=schemas.ProcessoResponse)
async def update_processo(
    processo_id: int,
    processo_update: schemas.ProcessoUpdate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await update_processo_service(db, processo_id, processo_update, current_user.escritorio_id)

@router.delete("/{processo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_processo(
    processo_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await delete_processo_service(db, processo_id, current_user.escritorio_id)
    return None

@router.post("/{processo_id}/atualizar-datajud", response_model=schemas.ProcessoResponse)
async def update_processo_datajud(
    processo_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await atualizar_processo_datajud_service(
        db, processo_id, current_user.escritorio_id, current_user.id
    )
