import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import schemas
import models
import crud
from services.storage_service import get_storage_provider

async def create_escritorio_service(db: AsyncSession, escritorio_in: schemas.EscritorioCreate):
    escritorio = models.Escritorio(**escritorio_in.model_dump())
    db.add(escritorio)
    try:
        await db.commit()
        await db.refresh(escritorio)
        return escritorio
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar escritório")

async def get_meu_escritorio_service(db: AsyncSession, current_user: models.Usuario):
    escritorio = await crud.get_escritorio(db, current_user.escritorio_id)
    if not escritorio:
        raise HTTPException(status_code=404, detail="Escritório não encontrado")
    return escritorio

async def update_meu_escritorio_service(
    db: AsyncSession, 
    current_user: models.Usuario, 
    nome: str, 
    documento: str, 
    gemini_api_key: str,
    logo: UploadFile
):
    if not (current_user.is_admin or current_user.perfil == 'Admin'):
        raise HTTPException(status_code=403, detail="Apenas administradores podem alterar os dados do escritório.")
        
    update_data = {
        "nome": nome,
        "documento": documento,
        "gemini_api_key": gemini_api_key
    }
    
    if logo:
        escritorio = await crud.get_escritorio(db, current_user.escritorio_id)
        storage = get_storage_provider(escritorio)
        
        # Extrair extensão e montar o nome do arquivo baseado no ID do escritório
        ext = logo.filename.split('.')[-1].lower() if '.' in logo.filename else 'png'
        filename = f"logo_{current_user.escritorio_id}.{ext}"
        
        content = await logo.read()
        # Salva usando o provedor de storage na subpasta 'logos'
        db_path = await storage.save_file(content, "logos", filename)
        update_data["logo_path"] = db_path
        
    escritorio_update = schemas.EscritorioUpdate(**update_data)
    
    updated_escritorio = await crud.update_escritorio(db, current_user.escritorio_id, escritorio_update)
    if not updated_escritorio:
        raise HTTPException(status_code=404, detail="Escritório não encontrado")
        
    return updated_escritorio

async def get_dashboard_stats_service(db: AsyncSession, current_user: models.Usuario):
    return await crud.get_dashboard_stats(db, escritorio_id=current_user.escritorio_id)
