import os
import shutil
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import schemas
import models
import crud

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
    logo_path = None
    if logo:
        # Extrair extensão e montar o nome do arquivo baseado no ID do escritório
        ext = logo.filename.split('.')[-1] if '.' in logo.filename else 'png'
        filename = f"logo_{current_user.escritorio_id}.{ext}"
        
        # Garantir que a pasta static/logos exista
        os.makedirs("static/logos", exist_ok=True)
        file_path = os.path.join("static/logos", filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
            
        logo_path = f"logos/{filename}" # Caminho relativo servido pelo mount /static
        
    escritorio_update = schemas.EscritorioUpdate(
        nome=nome,
        documento=documento,
        gemini_api_key=gemini_api_key,
        logo_path=logo_path
    )
    
    updated_escritorio = await crud.update_escritorio(db, current_user.escritorio_id, escritorio_update)
    if not updated_escritorio:
        raise HTTPException(status_code=404, detail="Escritório não encontrado")
        
    return updated_escritorio
