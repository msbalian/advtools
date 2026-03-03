from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.documento_service import (
    listar_modelos_service,
    criar_modelo_service,
    deletar_modelo_service,
    substituir_modelo_service,
    read_documentos_cliente_service,
    read_documentos_escritorio_service,
    read_documento_service,
    upload_documento_cliente_service,
    upload_documento_escritorio_service,
    update_documento_file_service,
    delete_documento_service,
    gerar_documento_service
)

router_modelos = APIRouter(prefix="/api/modelos", tags=["Modelos"])
router_documentos = APIRouter(prefix="/api/documentos", tags=["Documentos"])
router_clientes_docs = APIRouter(prefix="/api/clientes", tags=["Documentos"])
router_redator = APIRouter(prefix="/api/redator", tags=["Documentos"])

# --- MODELOS ---
@router_modelos.get("")
async def listar_modelos(db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await listar_modelos_service(db, current_user.escritorio_id)

@router_modelos.post("")
async def criar_modelo(
    nome: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await criar_modelo_service(db, current_user, nome, file)

@router_modelos.delete("/{modelo_id}")
async def deletar_modelo(modelo_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await deletar_modelo_service(db, current_user, modelo_id)

@router_modelos.put("/{modelo_id}")
async def substituir_modelo(
    modelo_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await substituir_modelo_service(db, current_user, modelo_id, file)

# --- DOCUMENTOS CLIENTE ---

@router_clientes_docs.get("/{cliente_id}/documentos", response_model=List[schemas.DocumentoCliente])
async def read_documentos_cliente(cliente_id: int, pasta_id: int = -1, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await read_documentos_cliente_service(db, current_user, cliente_id, pasta_id)

@router_clientes_docs.post("/{cliente_id}/documentos", response_model=schemas.DocumentoCliente)
async def upload_documento_cliente(
    cliente_id: int,
    nome: str = Form(...),
    pasta_id: int = Form(-1),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await upload_documento_cliente_service(db, current_user, cliente_id, file, nome, pasta_id=pasta_id)

# --- DOCUMENTOS ESCRITÓRIO ---

@router_documentos.get("/escritorio", response_model=List[schemas.DocumentoCliente])
async def read_documentos_escritorio(pasta_id: int = -1, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await read_documentos_escritorio_service(db, current_user, pasta_id)

@router_documentos.post("/escritorio", response_model=schemas.DocumentoCliente)
async def upload_documento_escritorio(
    nome: str = Form(...),
    pasta_id: int = Form(-1),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await upload_documento_escritorio_service(db, current_user, file, nome, pasta_id=pasta_id)

@router_documentos.get("/{documento_id}", response_model=schemas.DocumentoCliente)
async def read_documento(documento_id: int, current_user: models.Usuario = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await read_documento_service(db, current_user, documento_id)

@router_documentos.put("/{documento_id}", response_model=schemas.DocumentoCliente)
async def update_documento_file(
    documento_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user)
):
    return await update_documento_file_service(db, current_user, documento_id, file)

@router_documentos.delete("/{documento_id}", status_code=204)
async def delete_documento(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    await delete_documento_service(db, current_user, documento_id)
    return None

# --- REDATOR INTELIGENTE ---

@router_redator.post("/gerar", response_model=schemas.DocumentoCliente)
async def gerar_documento(
    request: schemas.GerarDocumentoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return await gerar_documento_service(db, current_user, request)
