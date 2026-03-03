from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import schemas
import models
import crud
from database import get_db
from services.auth_service import get_current_user
from services import organizador_service
from services.job_manager import job_manager

router = APIRouter(prefix="/api/pastas", tags=["Pastas de Documentos"])

@router.get("", response_model=List[schemas.PastaDocumentoResponse])
async def listar_pastas(
    cliente_id: Optional[int] = None,
    servico_id: Optional[int] = None,
    parent_id: Optional[int] = -1,
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.get_pastas(db, current_user.escritorio_id, cliente_id, servico_id, parent_id)

@router.post("", response_model=schemas.PastaDocumentoResponse)
async def criar_pasta(
    pasta: schemas.PastaDocumentoCreate,
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.create_pasta(db, pasta, current_user.escritorio_id)

@router.put("/{pasta_id}", response_model=schemas.PastaDocumentoResponse)
async def atualizar_pasta(
    pasta_id: int,
    pasta_update: schemas.PastaDocumentoUpdate,
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    db_pasta = await crud.update_pasta(db, pasta_id, pasta_update, current_user.escritorio_id)
    if not db_pasta:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return db_pasta

@router.delete("/{pasta_id}")
async def deletar_pasta(
    pasta_id: int,
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    success, message = await crud.delete_pasta(db, pasta_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}

@router.post("/{pasta_id}/organizar")
async def organizar_pasta(
    pasta_id: int, 
    background_tasks: BackgroundTasks,
    current_user: models.Usuario = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    return await organizador_service.iniciar_organizacao_pasta(db, current_user, pasta_id, background_tasks)

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, current_user: models.Usuario = Depends(get_current_user)):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job
