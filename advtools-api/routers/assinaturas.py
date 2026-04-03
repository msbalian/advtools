from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import schemas
import models
from database import get_db
from services.auth_service import get_current_user
from services.assinatura_service import (
    read_signatarios_service,
    create_signatario_service,
    delete_signatario_service,
    update_signatario_posicao_service,
    finalizar_documento_service,
    preview_pdf_service,
    public_get_sala_assinatura_service,
    public_confirm_assinatura_service,
    public_validar_documento_service
)

router_assinaturas = APIRouter(prefix="/api/documentos", tags=["Assinaturas"])
router_assinativas_public = APIRouter(prefix="/api/public", tags=["Assinaturas Públicas"])

# --- GESTÃO DE ASSINATURAS (LOGADA) ---

@router_assinaturas.get("/{documento_id}/signatarios", response_model=List[schemas.SignatarioResponse])
async def read_signatarios(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await read_signatarios_service(db, current_user, documento_id)

@router_assinaturas.post("/{documento_id}/signatarios", response_model=schemas.SignatarioResponse)
async def create_signatario(documento_id: int, signatario: schemas.SignatarioCreate, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await create_signatario_service(db, current_user, documento_id, signatario)

@router_assinaturas.delete("/{documento_id}/signatarios/{signatario_id}")
async def delete_signatario(documento_id: int, signatario_id: int, request: Request, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    base_url = str(request.base_url).rstrip('/')
    return await delete_signatario_service(db, current_user, documento_id, signatario_id, base_url)

@router_assinaturas.put("/{documento_id}/signatarios/{signatario_id}/posicao")
async def update_signatario_posicao(documento_id: int, signatario_id: int, posicao: schemas.SignatarioPosicoesUpdate, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await update_signatario_posicao_service(db, current_user, documento_id, signatario_id, posicao)

@router_assinaturas.post("/{documento_id}/finalizar")
async def finalizar_documento(documento_id: int, db: AsyncSession = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return await finalizar_documento_service(db, current_user, documento_id)

# --- ROTAS PÚBLICAS (NÃO LOGADAS) ---

@router_assinativas_public.get("/assinar/preview-pdf/{documento_id}")
async def preview_pdf(documento_id: int, db: AsyncSession = Depends(get_db)):
    return await preview_pdf_service(db, documento_id)

@router_assinativas_public.get("/assinar/{token}")
async def public_get_sala_assinatura(token: str, db: AsyncSession = Depends(get_db)):
    return await public_get_sala_assinatura_service(db, token)

@router_assinativas_public.post("/assinar/{token}/confirmar")
async def public_confirm_assinatura(token: str, data: schemas.AssinaturaConfirmarRequest, request: Request, db: AsyncSession = Depends(get_db)):
    host_ip = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("user-agent", "Unknown")
    base_url = str(request.base_url).rstrip('/')
    return await public_confirm_assinatura_service(db, token, data, host_ip, user_agent, base_url)

@router_assinativas_public.get("/validar/{token_validacao}")
async def public_validar_documento(token_validacao: str, db: AsyncSession = Depends(get_db)):
    return await public_validar_documento_service(db, token_validacao)
