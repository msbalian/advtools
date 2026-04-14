from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List

import schemas
import models
from database import get_db
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/ultimas-movimentacoes", response_model=schemas.DashboardMovimentacaoPaginatedResponse)
async def get_ultimas_movimentacoes(
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    Retorna as últimas movimentações de todos os processos do escritório do usuário logado, de forma paginada.
    """
    from sqlalchemy import func
    
    # Busca o total
    total_result = await db.execute(
        select(func.count(models.Movimentacao.id))
        .join(models.Processo)
        .filter(models.Processo.escritorio_id == current_user.escritorio_id)
    )
    total = total_result.scalar() or 0

    # Busca os itens paginados
    result = await db.execute(
        select(models.Movimentacao)
        .join(models.Processo)
        .options(
            selectinload(models.Movimentacao.processo)
            .selectinload(models.Processo.cliente)
        )
        .filter(models.Processo.escritorio_id == current_user.escritorio_id)
        .order_by(desc(models.Movimentacao.data_hora))
        .offset(skip)
        .limit(limit)
    )
    movs = result.scalars().all()
    
    return {"items": movs, "total": total}
