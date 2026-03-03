import os
import io
import uuid as _uuid
import base64
from datetime import datetime
from typing import List
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sql_select, func as sql_func, update as sql_update
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

import schemas
import models
import crud
import assinador_service
from services.documento_service import convert_docx_to_pdf_async
from services.storage_service import get_storage_provider

# --- GESTÃO DE ASSINATURAS (LOGADA) ---

async def read_signatarios_service(db: AsyncSession, current_user: models.Usuario, documento_id: int):
    signatarios = await crud.get_signatarios(db, documento_id, current_user.escritorio_id)
    if signatarios is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return signatarios

async def create_signatario_service(db: AsyncSession, current_user: models.Usuario, documento_id: int, signatario: schemas.SignatarioCreate):
    db_sig = await crud.create_signatario(db, documento_id, signatario, current_user.escritorio_id)
    if not db_sig:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return db_sig

async def delete_signatario_service(db: AsyncSession, current_user: models.Usuario, documento_id: int, signatario_id: int):
    success = await crud.delete_signatario(db, documento_id, signatario_id, current_user.escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Signatário não encontrado ou não autorizado")
    return {"message": "Signatário removido"}

async def update_signatario_posicao_service(db: AsyncSession, current_user: models.Usuario, documento_id: int, signatario_id: int, posicao: schemas.SignatarioPosicoesUpdate):
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    updated = await crud.update_signatario_posicao(db, signatario_id, posicao)
    if not updated:
        raise HTTPException(status_code=404, detail="Signatário não encontrado")
    return {"message": "Posições salvas com sucesso"}

async def finalizar_documento_service(db: AsyncSession, current_user: models.Usuario, documento_id: int):
    doc = await crud.get_documento_by_id(db, documento_id, current_user.escritorio_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    signatarios = await crud.get_signatarios(db, documento_id, current_user.escritorio_id)
    pendentes = [s for s in signatarios if s.status != 'Assinado']
    
    if pendentes:
        raise HTTPException(status_code=400, detail="Ainda há assinaturas pendentes.")
        
    if doc.status_assinatura != 'Concluido':
        doc.status_assinatura = 'Concluido'
        if not doc.token_validacao:
            doc.token_validacao = _uuid.uuid4().hex
        db.add(doc)
        await db.commit()
        
    return {"message": "Processamento concluído", "status": "Concluido"}


# --- ROTAS PÚBLICAS (NÃO LOGADAS) ---

async def preview_pdf_service(db: AsyncSession, documento_id: int):
    res = await db.execute(sql_select(models.DocumentoCliente).filter(models.DocumentoCliente.id == documento_id))
    doc = res.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    escritorio = await crud.get_escritorio(db, doc.escritorio_id)
    storage = get_storage_provider(escritorio)
    
    # Resolve o caminho físico (suporta legado e novo formato)
    arquivo_original = f"static/{doc.arquivo_path}"
    if not os.path.exists(arquivo_original):
        # Tenta no subdiretório de armazenamento
        alt_path = f"static/armazenamento/{doc.arquivo_path}"
        if os.path.exists(alt_path):
            arquivo_original = alt_path
            
    arquivo_exibicao = arquivo_original
    
    if arquivo_original.lower().endswith('.docx'):
        pdf_path = arquivo_original.replace('.docx', '_visualizacao.pdf')
        if not os.path.exists(pdf_path) and os.path.exists(arquivo_original):
            try:
                await convert_docx_to_pdf_async(arquivo_original, pdf_path)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF para visualização: {e}")
        
        if os.path.exists(pdf_path):
            arquivo_exibicao = pdf_path
            
    if not os.path.exists(arquivo_exibicao):
        # Se for Drive, poderíamos retornar uma URL de Redirecionamento 
        # mas o componente PDF do Vue precisa do stream do arquivo.
        raise HTTPException(status_code=404, detail="Arquivo físico de visualização não encontrado")
        
    return FileResponse(arquivo_exibicao, media_type="application/pdf")

async def public_get_sala_assinatura_service(db: AsyncSession, token: str):
    sig = await crud.get_signatario_by_token(db, token)
    if not sig:
        raise HTTPException(status_code=404, detail="Link inválido ou expirado")
        
    res = await db.execute(select(models.DocumentoCliente).filter(models.DocumentoCliente.id == sig.documento_id))
    doc = res.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento indisponível")
        
    if sig.status == 'Pendente':
        sig.status = 'Visualizado'
        sig.data_visualizacao = datetime.now()
        db.add(sig)
        await db.commit()
        
    # Resolve o caminho físico
    arquivo_original = f"static/{doc.arquivo_path}"
    if not os.path.exists(arquivo_original):
        alt_path = f"static/armazenamento/{doc.arquivo_path}"
        if os.path.exists(alt_path):
            arquivo_original = alt_path
            
    arquivo_exibicao = arquivo_original
    
    if arquivo_original.lower().endswith('.docx'):
        pdf_path = arquivo_original.replace('.docx', '_visualizacao.pdf')
        if not os.path.exists(pdf_path) and os.path.exists(arquivo_original):
            try:
                await convert_docx_to_pdf_async(arquivo_original, pdf_path)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF para visualização: {e}")
        
        if os.path.exists(pdf_path):
            arquivo_exibicao = pdf_path
            
    return {
        "signatario": {
            "id": sig.id,
            "nome": sig.nome,
            "email": sig.email,
            "cpf": sig.cpf,
            "status": sig.status,
            "funcao": sig.funcao
        },
        "documento": {
            "id": doc.id,
            "nome": doc.nome,
            "arquivo_url": f"/{arquivo_exibicao}",
            "status_assinatura": doc.status_assinatura
        }
    }

async def public_confirm_assinatura_service(db: AsyncSession, token: str, data: schemas.AssinaturaConfirmarRequest, host_ip: str, user_agent: str, base_url: str):
    sig = await crud.get_signatario_by_token(db, token)
    if not sig:
        raise HTTPException(status_code=404, detail="Link inválido ou expirado")

    doc_id = sig.documento_id
    doc_res = await db.execute(sql_select(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id))
    doc = doc_res.scalars().first()
    if not doc:
        return {"message": "O documento já foi removido."}

    ja_assinado = sig.status == 'Assinado'
    if ja_assinado and doc.status_assinatura == 'Concluido':
        return {"message": "Documento já assinado por este signatário e finalizado."}

    if not ja_assinado:
        escritorio = await crud.get_escritorio(db, doc.escritorio_id)
        storage = get_storage_provider(escritorio)
        
        img_filename = f"{data.tipo_autenticacao}_{sig.token_acesso}.png"
        
        try:
            encoded_data = data.imagem_base64.split(",")[1] if "," in data.imagem_base64 else data.imagem_base64
            decoded_data = base64.b64decode(encoded_data)
            
            # Salva no storage (local ou drive)
            db_img_path = await storage.save_file(decoded_data, "assinaturas", img_filename)
        except Exception as e:
            print(f"Erro ao salvar imagem da assinatura: {e}")
            raise HTTPException(status_code=400, detail="Erro ao processar imagem da assinatura")

        sig.imagem_assinatura_path = db_img_path
        sig.tipo_autenticacao = data.tipo_autenticacao
        sig.status = 'Assinado'
        sig.data_assinatura = datetime.now()
        if data.cpf and not sig.cpf:
            sig.cpf = data.cpf
        sig.ip_assinatura = host_ip
        sig.user_agent_assinatura = user_agent
        
        if data.pos_page is not None:
            sig.page_number = data.pos_page
            sig.x_pos = data.pos_x
            sig.y_pos = data.pos_y
            sig.width = data.pos_width
            sig.height = data.pos_height
            sig.docWidth = data.pos_doc_width
            sig.docHeight = data.pos_doc_height
            
        db.add(sig)
        await db.commit()

    total_res = await db.execute(sql_select(sql_func.count()).select_from(models.Signatario).where(models.Signatario.documento_id == doc_id))
    assinados_res = await db.execute(sql_select(sql_func.count()).select_from(models.Signatario).where(models.Signatario.documento_id == doc_id, models.Signatario.status == 'Assinado'))
    total = total_res.scalar() or 0
    assinados = assinados_res.scalar() or 0

    if assinados < total:
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(status_assinatura='Parcial'))
        await db.commit()
        return {"message": "Assinatura confirmada com sucesso!"}

    PASTA_TEMPORARIA = "static/temp"
    os.makedirs(PASTA_TEMPORARIA, exist_ok=True)

    escritorio = await crud.get_escritorio(db, doc.escritorio_id)
    storage = get_storage_provider(escritorio)

    caminho_original = os.path.join("static", doc.arquivo_path)
    if not os.path.exists(caminho_original):
        # Fallback para nova estrutura se necessário
        caminho_original = os.path.join("static/armazenamento", doc.arquivo_path)

    caminho_pdf_base = caminho_original

    if caminho_original.lower().endswith('.docx'):
        caminho_pdf_base = caminho_original.replace('.docx', '_converted.pdf')
        if not os.path.exists(caminho_pdf_base):
            try:
                await convert_docx_to_pdf_async(caminho_original, caminho_pdf_base)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF: {e}")
                caminho_pdf_base = None

    # Lemos os bytes do PDF base
    if not caminho_pdf_base or not os.path.exists(caminho_pdf_base):
         raise HTTPException(status_code=500, detail="Erro ao preparar PDF base para assinatura.")
    
    with open(caminho_pdf_base, "rb") as f:
        pdf_base_bytes = f.read()

    sigs_res = await db.execute(
        select(models.Signatario)
        .options(selectinload(models.Signatario.posicoes))
        .where(models.Signatario.documento_id == doc_id)
    )
    todos_sigs = sigs_res.scalars().all()
    
    sigs_list_flat = []
    sigs_list_unique = []
    
    for s in todos_sigs:
        base_sig_dict = {
            "id": s.id,
            "nome": s.nome,
            "email": s.email,
            "cpf": s.cpf or "Não informado",
            "funcao": s.funcao,
            "status": s.status,
            "tipo_autenticacao": s.tipo_autenticacao,
            "data_assinatura": s.data_assinatura,
            "ip_assinatura": s.ip_assinatura,
            "user_agent_assinatura": s.user_agent_assinatura,
            "imagem_assinatura_path": s.imagem_assinatura_path,
            "pos_page": s.page_number,
            "pos_x": s.x_pos,
            "pos_y": s.y_pos,
            "pos_width": s.width,
            "pos_height": s.height,
            "pos_doc_width": s.docWidth,
            "pos_doc_height": s.docHeight,
        }
        
        sigs_list_unique.append(base_sig_dict)
        
        if hasattr(s, 'posicoes') and s.posicoes and len(s.posicoes) > 0:
            for p in s.posicoes:
                pos_sig = base_sig_dict.copy()
                pos_sig.update({
                    "pos_page": p.page_number,
                    "pos_x": p.x_pos,
                    "pos_y": p.y_pos,
                    "pos_width": p.width,
                    "pos_height": p.height,
                    "pos_doc_width": p.docWidth,
                    "pos_doc_height": p.docHeight,
                })
                sigs_list_flat.append(pos_sig)
        else:
            sigs_list_flat.append(base_sig_dict)

    # Estampar assinaturas em memória
    try:
        pdf_estampado_bytes = assinador_service.estampar_assinaturas(pdf_base_bytes, sigs_list_flat)
    except Exception as e:
        print(f"Erro ao estampar: {e}")
        pdf_estampado_bytes = pdf_base_bytes

    if not doc.token_validacao:
        new_token = _uuid.uuid4().hex
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(token_validacao=new_token))
        await db.commit()
        doc.token_validacao = new_token

    url_validacao = f"{base_url}/api/public/validar/{doc.token_validacao}"

    hash_orig = doc.hash_original
    if not hash_orig:
        hash_orig = assinador_service.calcular_hash_bytes(pdf_base_bytes)
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(hash_original=hash_orig))
        await db.commit()

    # Gerar Certificado em memória
    doc_dict = {
        "nome": doc.nome,
        "hash_original": hash_orig or "N/A"
    }
    try:
        certificado_bytes = assinador_service.gerar_certificado_pdf(doc_dict, sigs_list_unique, url_validacao=url_validacao)
    except Exception as e:
        print(f"Erro ao gerar certificado: {e}")
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(status_assinatura='Concluido'))
        await db.commit()
        return {"message": "Assinatura confirmada. Erro ao gerar certificado."}

    # Mesclar Estampado + Certificado
    final_pdf_bytes = b""
    try:
        writer = assinador_service.PdfWriter()
        # Documento com assinaturas estampadas
        reader_estampado = assinador_service.PdfReader(io.BytesIO(pdf_estampado_bytes))
        for page in reader_estampado.pages:
            writer.add_page(page)
            
        # Manifesto/Certificado
        reader_cert = assinador_service.PdfReader(io.BytesIO(certificado_bytes))
        for page in reader_cert.pages:
            writer.add_page(page)
        
        out_stream = io.BytesIO()
        writer.write(out_stream)
        final_pdf_bytes = out_stream.getvalue()
    except Exception as e:
        print(f"ERRO CRÍTICO AO ANEXAR CERTIFICADO: {str(e)}")
        # Fallback para o documento estampado se a mesclagem falhar
        final_pdf_bytes = pdf_estampado_bytes

    # Salvar o Documento Final Assinado no Storage
    nome_final = f"assinado_{doc.id}_{_uuid.uuid4().hex[:6]}.pdf"
    if doc.cliente_id:
        relative_dir = f"cliente_{doc.cliente_id}/assinados"
    else:
        relative_dir = "escritorio/documentos/assinados"
    
    db_final_path = await storage.save_file(final_pdf_bytes, relative_dir, nome_final)
    hash_final = assinador_service.calcular_hash_bytes(final_pdf_bytes)

    await db.execute(
        sql_update(models.DocumentoCliente)
        .where(models.DocumentoCliente.id == doc_id)
        .values(
            status_assinatura='Concluido',
            arquivo_assinado_path=db_final_path,
            hash_assinado=hash_final
        )
    )
    await db.commit()

    return {"message": "Assinatura confirmada e documento finalizado!"}

async def public_validar_documento_service(db: AsyncSession, token_validacao: str):
    doc = await crud.get_documentacao_by_validacao(db, token_validacao)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    return {
        "nome": doc.nome,
        "status_assinatura": doc.status_assinatura,
        "hash_original": doc.hash_original,
        "hash_assinado": doc.hash_assinado,
        "data_criacao": doc.data_criacao.isoformat() if doc.data_criacao else None
    }
