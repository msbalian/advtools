from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import crud
import schemas
from database import get_db
from services.auth_service import get_current_user
import models

router = APIRouter(
    prefix="/api/configuracoes",
    tags=["configuracoes"]
)

# ==========================
# PASTAS DE TRABALHO
# ==========================

@router.get("/pastas-trabalho", response_model=List[schemas.PastaTrabalho])
async def read_pastas_trabalho(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.get_pastas_trabalho(db, escritorio_id=current_user.escritorio_id)

@router.post("/pastas-trabalho", response_model=schemas.PastaTrabalho)
async def create_pasta_trabalho(
    pasta: schemas.PastaTrabalhoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.create_pasta_trabalho(db, pasta, escritorio_id=current_user.escritorio_id)

@router.delete("/pastas-trabalho/{pasta_id}")
async def delete_pasta_trabalho(
    pasta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    success = await crud.delete_pasta_trabalho(db, pasta_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pasta de trabalho não encontrada")
    return {"message": "Pasta excluída com sucesso"}

# ==========================
# TIPOS DE SERVIÇO
# ==========================

@router.get("/tipos-servico", response_model=List[schemas.TipoServico])
async def read_tipos_servico(
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.get_tipos_servico(db, escritorio_id=current_user.escritorio_id)

@router.post("/tipos-servico", response_model=schemas.TipoServico)
async def create_tipo_servico(
    tipo: schemas.TipoServicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return await crud.create_tipo_servico(db, tipo, escritorio_id=current_user.escritorio_id)

@router.delete("/tipos-servico/{tipo_id}")
async def delete_tipo_servico(
    tipo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    success = await crud.delete_tipo_servico(db, tipo_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de serviço não encontrado")
    return {"message": "Tipo de serviço excluído com sucesso"}
