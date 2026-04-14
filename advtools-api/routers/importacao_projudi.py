"""Router para importação em massa de processos do PROJUDI."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.auth_service import get_current_user
import schemas
from services.processo_service import importar_massa_projudi_service

router = APIRouter(prefix="/api/importacao", tags=["Importação PROJUDI"])


@router.post("/projudi", response_model=schemas.ImportacaoRelatorio)
async def importar_projudi(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Importa em massa todos os processos com avisos pendentes do PROJUDI."""
    return await importar_massa_projudi_service(
        db,
        escritorio_id=current_user.escritorio_id,
        usuario_id=current_user.id,
    )
