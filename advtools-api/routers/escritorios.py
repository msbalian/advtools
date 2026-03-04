from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.escritorio_service import (
    create_escritorio_service,
    get_meu_escritorio_service,
    update_meu_escritorio_service,
    get_dashboard_stats_service
)

router = APIRouter(prefix="/api/escritorios", tags=["Escritorios"])
router_singular = APIRouter(prefix="/api/escritorio", tags=["Escritorios"])

@router.post("", response_model=schemas.Escritorio)
async def create_escritorio(escritorio_in: schemas.EscritorioCreate, db: AsyncSession = Depends(get_db)):
    return await create_escritorio_service(db, escritorio_in)

@router_singular.get("", response_model=schemas.Escritorio)
async def get_meu_escritorio(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_meu_escritorio_service(db, current_user)

@router_singular.put("", response_model=schemas.Escritorio)
async def update_meu_escritorio(
    nome: str = Form(...),
    documento: str = Form(None),
    gemini_api_key: str = Form(None),
    logo: UploadFile = File(None),
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await update_meu_escritorio_service(db, current_user, nome, documento, gemini_api_key, logo)

@router_singular.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_dashboard_stats_service(db, current_user)
