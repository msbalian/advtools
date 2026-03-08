from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

import schemas
import models
import crud
from database import get_db
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/financeiro", tags=["Financeiro"])

@router.get("/fluxo", response_model=schemas.FluxoCaixaMes)
async def get_fluxo(
    mes: int = Query(default=datetime.now().month),
    ano: int = Query(default=datetime.now().year),
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_fluxo_caixa(db, current_user.escritorio_id, mes, ano)

@router.get("/transacoes", response_model=List[schemas.TransacaoResponse])
async def read_transacoes(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_transacoes(db, current_user.escritorio_id, mes, ano)

@router.post("/transacoes", response_model=schemas.TransacaoResponse)
async def create_transacao(
    transacao: schemas.TransacaoCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_transacao(db, transacao, current_user.escritorio_id)

@router.put("/transacoes/{transacao_id}", response_model=schemas.TransacaoResponse)
async def update_transacao(
    transacao_id: int,
    transacao: schemas.TransacaoUpdate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_transacao = await crud.update_transacao(db, transacao_id, transacao, current_user.escritorio_id)
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return db_transacao

@router.delete("/transacoes/{transacao_id}", status_code=204)
async def delete_transacao(
    transacao_id: int,
    delete_series: bool = Query(default=False),
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_transacao(db, transacao_id, current_user.escritorio_id, delete_series)
    if not success:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return None

# ==========================
# CATEGORIAS FINANCEIRAS
# ==========================

@router.get("/categorias", response_model=List[schemas.CategoriaFinanceiraResponse])
async def get_categorias(
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_categorias_financeiras(db, current_user.escritorio_id)

@router.post("/categorias", response_model=schemas.CategoriaFinanceiraResponse)
async def create_categoria(
    categoria: schemas.CategoriaFinanceiraCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_categoria_financeira(db, categoria, current_user.escritorio_id)

@router.put("/categorias/{categoria_id}", response_model=schemas.CategoriaFinanceiraResponse)
async def update_categoria(
    categoria_id: int,
    categoria: schemas.CategoriaFinanceiraCreate,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_categoria = await crud.update_categoria_financeira(db, categoria_id, categoria, current_user.escritorio_id)
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return db_categoria

@router.delete("/categorias/{categoria_id}", status_code=204)
async def delete_categoria(
    categoria_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_categoria_financeira(db, categoria_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return None
