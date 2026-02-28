import os
import uuid as _uuid
import base64
from datetime import datetime
from typing import List
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sql_select, func as sql_func, update as sql_update
from sqlalchemy.future import select

import schemas
import models
import crud
import assinador_service
from services.documento_service import convert_docx_to_pdf_async

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
    # Preview endpoint can be used securely if token is verified, but currently requested purely by doc id
    res = await db.execute(sql_select(models.DocumentoCliente).filter(models.DocumentoCliente.id == documento_id))
    doc = res.scalars().first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
        
    arquivo_original = f"static/{doc.arquivo_path}"
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
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado")
        
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
        
    arquivo_original = f"static/{doc.arquivo_path}"
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
        upload_dir = "static/assinaturas"
        os.makedirs(upload_dir, exist_ok=True)
        img_filename = f"{data.tipo_autenticacao}_{sig.token_acesso}.png"
        img_path = os.path.join(upload_dir, img_filename)

        try:
            encoded_data = data.imagem_base64.split(",")[1] if "," in data.imagem_base64 else data.imagem_base64
            decoded_data = base64.b64decode(encoded_data)
            with open(img_path, "wb") as f:
                f.write(decoded_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Base64 inválido")

        sig.imagem_assinatura_path = img_path
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

    PASTA_SAIDA = "static/documentos_assinados"
    os.makedirs(PASTA_SAIDA, exist_ok=True)

    caminho_original = os.path.join("static", doc.arquivo_path)
    caminho_pdf_base = caminho_original

    if caminho_original.lower().endswith('.docx'):
        caminho_pdf_base = caminho_original.replace('.docx', '_converted.pdf')
        if not os.path.exists(caminho_pdf_base):
            try:
                await convert_docx_to_pdf_async(caminho_original, caminho_pdf_base)
            except Exception as e:
                print(f"Erro ao converter DOCX para PDF: {e}")
                caminho_pdf_base = None

    sigs_res = await db.execute(select(models.Signatario).where(models.Signatario.documento_id == doc_id))
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

    caminho_estampado = caminho_pdf_base
    if caminho_pdf_base and os.path.exists(caminho_pdf_base):
        caminho_estampado_temp = os.path.join(PASTA_SAIDA, f"estampado_{doc_id}.pdf")
        try:
            caminho_estampado = assinador_service.estampar_assinaturas(caminho_pdf_base, sigs_list_flat, caminho_estampado_temp)
        except Exception as e:
            print(f"Erro ao estampar: {e}")
            caminho_estampado = caminho_pdf_base

    if not doc.token_validacao:
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(token_validacao=_uuid.uuid4().hex))
        await db.commit()
        doc_res2 = await db.execute(select(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id))
        doc = doc_res2.scalars().first()

    url_validacao = f"{base_url}/api/public/validar/{doc.token_validacao}"

    hash_orig = doc.hash_original
    if not hash_orig and caminho_pdf_base and os.path.exists(caminho_pdf_base):
        hash_orig = assinador_service.calcular_hash_arquivo(caminho_pdf_base)
        if hash_orig:
            await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(hash_original=hash_orig))
            await db.commit()

    caminho_certificado = os.path.join(PASTA_SAIDA, f"certificado_{doc_id}.pdf")
    doc_dict = {
        "nome": doc.nome,
        "hash_original": hash_orig or "N/A"
    }
    try:
        assinador_service.gerar_certificado_pdf(doc_dict, sigs_list_unique, caminho_certificado, url_validacao)
    except Exception as e:
        print(f"Erro ao gerar certificado: {e}")
        await db.execute(sql_update(models.DocumentoCliente).where(models.DocumentoCliente.id == doc_id).values(status_assinatura='Concluido'))
        await db.commit()
        return {"message": "Assinatura confirmada. Erro ao gerar certificado."}

    nome_final = f"final_assinado_{doc_id}.pdf"
    caminho_final = os.path.join(PASTA_SAIDA, nome_final)

    if caminho_estampado and os.path.exists(caminho_estampado):
        try:
            assinador_service.anexar_certificado(caminho_estampado, caminho_certificado, caminho_final)
        except Exception as e:
            print(f"Erro ao anexar certificado: {e}")
            caminho_final = caminho_certificado
    else:
        caminho_final = caminho_certificado

    hash_final = assinador_service.calcular_hash_arquivo(caminho_final)
    arquivo_path_relativo = caminho_final.replace("static/", "", 1) if caminho_final.startswith("static/") else caminho_final

    await db.execute(
        sql_update(models.DocumentoCliente)
        .where(models.DocumentoCliente.id == doc_id)
        .values(
            status_assinatura='Concluido',
            arquivo_assinado_path=arquivo_path_relativo,
            hash_assinado=hash_final
        )
    )
    await db.commit()

    for tmp in [caminho_estampado]:
        if tmp and tmp != caminho_final and tmp != caminho_pdf_base:
            try:
                os.remove(tmp)
            except:
                pass

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
