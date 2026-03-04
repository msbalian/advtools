import os
import io
import uuid
import json
import logging
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, BackgroundTasks
from openpyxl import Workbook
from pypdf import PdfReader
from docx import Document
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

import models
import crud
import schemas
from services.ai_service import analisar_documento_para_organizacao
from services.storage_service import get_storage_provider
from services.job_manager import job_manager
from config import Config

logger = logging.getLogger(__name__)

async def extrair_texto_documento(file_path: str) -> str:
    """Extrai texto de PDF ou DOCX."""
    if not os.path.exists(file_path):
        return ""
    
    ext = file_path.split('.')[-1].lower()
    texto = ""
    
    try:
        if ext == 'pdf':
            reader = PdfReader(file_path)
            for i in range(min(3, len(reader.pages))):
                texto += reader.pages[i].extract_text() + "\n"
        elif ext == 'docx':
            doc = Document(file_path)
            for i, para in enumerate(doc.paragraphs):
                if i > 50: break
                texto += para.text + "\n"
    except Exception as e:
        logger.error(f"Erro ao extrair texto de {file_path}: {e}")
        
    return texto.strip()

def converter_imagem_para_pdf(image_path: str) -> bytes:
    """Converte uma imagem para PDF usando Pillow e ReportLab."""
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_width, img_height = img.size
    aspect = img_height / float(img_width)
    
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    
    # Redimensiona para caber na página A4 mantendo proporção
    if aspect > (height / width):
        new_height = height
        new_width = new_height / aspect
    else:
        new_width = width
        new_height = new_width * aspect
        
    c.drawImage(image_path, 0, height - new_height, width=new_width, height=new_height)
    c.showPage()
    c.save()
    return pdf_buffer.getvalue()

async def organizar_pasta_task(job_id: str, db_factory, current_user_id: int, escritorio_id: int, pasta_id: int):
    """Tarefa de background para organizar a pasta."""
    from database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # 1. Setup
            job_manager.update_job(job_id, status="running", message="Iniciando organização...")
            
            user_query = select(models.Usuario).filter(models.Usuario.id == current_user_id)
            user_result = await db.execute(user_query)
            current_user = user_result.scalar_one()

            pasta = await crud.get_pasta_by_id(db, pasta_id, escritorio_id)
            if not pasta:
                job_manager.update_job(job_id, status="failed", message="Pasta não encontrada")
                return

            query = select(models.DocumentoCliente).filter(models.DocumentoCliente.pasta_id == pasta_id)
            result = await db.execute(query)
            documentos = result.scalars().all()
            
            if not documentos:
                job_manager.update_job(job_id, status="completed", progress=100, message="Pasta vazia.")
                return

            escritorio = await crud.get_escritorio(db, escritorio_id)
            # Prioriza a chave do banco. Se não houver, avisa o usuário.
            api_key = escritorio.gemini_api_key if escritorio else None
            
            if not api_key:
                job_manager.update_job(job_id, status="failed", 
                                     message="Chave de API do Gemini não configurada. Por favor, cadastre sua chave nas Configurações do Escritório para usar o Organizador Inteligente.")
                return

            storage = get_storage_provider(escritorio)
            
            despesas = []
            total_docs = len(documentos)
            
            # 2. Processar cada documento
            for idx, doc in enumerate(documentos, 1):
                progress = int((idx / total_docs) * 90)
                job_manager.update_job(job_id, progress=progress, message=f"Processando {idx}/{total_docs}: {doc.nome}")
                
                source_path = os.path.join("static", doc.arquivo_path)
                if not os.path.exists(source_path):
                    source_path = os.path.join("static/armazenamento", doc.arquivo_path)
                if not os.path.exists(source_path): continue

                ext = doc.arquivo_path.split('.')[-1].lower()
                texto = ""
                image_b64 = None
                
                # Se for imagem, extrair base64 para o Gemini Vision
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    with open(source_path, "rb") as image_file:
                        image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
                        mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
                else:
                    texto = await extrair_texto_documento(source_path)
                    # Fallback para PDF escaneado (sem texto): tenta extrair primeira imagem
                    if not texto and ext == 'pdf':
                        try:
                            reader = PdfReader(source_path)
                            for page in reader.pages:
                                if page.images:
                                    img_obj = page.images[0]
                                    image_b64 = base64.b64encode(img_obj.data).decode('utf-8')
                                    mime_type = "image/jpeg" # pypdf costuma extrair como jpeg ou png
                                    break
                        except: pass

                # Chamar IA Multimodal
                metadados = await analisar_documento_para_organizacao(api_key, texto, image_b64, mime_type if image_b64 else None)
                
                if "error" in metadados:
                    logger.warning(f"IA falhou para {doc.id}: {metadados['error']}")
                    continue

                novo_nome_base = metadados.get("nome_sugerido", doc.nome)
                # Limpa caracteres especiais, mas mantém espaços e hífens para organização humana
                novo_nome_base = "".join([c for c in novo_nome_base if c.isalnum() or c in (' ', '_', '-')]).strip()
                novo_nome_exibicao = f"{idx:02d}. {novo_nome_base}"
                
                # Conversão para PDF se necessário
                final_content = None
                final_ext = "pdf"
                
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    job_manager.update_job(job_id, message=f"Convertendo {doc.nome} para PDF...")
                    final_content = converter_imagem_para_pdf(source_path)
                elif ext == 'docx':
                    job_manager.update_job(job_id, message=f"Extraindo conteúdo Word de {doc.nome}...")
                    final_ext = "docx" 
                    with open(source_path, 'rb') as f: final_content = f.read()
                else:
                    final_ext = ext
                    with open(source_path, 'rb') as f: final_content = f.read()

                novo_nome_arquivo = f"{idx:02d}_{novo_nome_base}_{uuid.uuid4().hex[:4]}.{final_ext}"
                target_dir = os.path.dirname(doc.arquivo_path)
                
                # Salvar novo arquivo
                new_db_path = await storage.save_file(final_content, target_dir, novo_nome_arquivo)
                await storage.delete_file(doc.arquivo_path)
                
                # Atualizar DB
                doc.nome = novo_nome_exibicao
                doc.arquivo_path = new_db_path
                doc.tamanho = len(final_content)
                from datetime import datetime
                doc.data_alteracao = datetime.now()
                
                if metadados.get("is_financeiro"):
                    despesas.append({
                        "arquivo": novo_nome_exibicao,
                        "data": metadados.get("data"),
                        "descricao": metadados.get("descricao"),
                        "valor": metadados.get("valor")
                    })
                
                # Atualiza progresso após completar o arquivo
                progress = int((idx / total_docs) * 95)
                job_manager.update_job(job_id, progress=progress)

            # 3. Planilha
            if despesas:
                job_manager.update_job(job_id, progress=95, message="Gerando planilha de despesas...")
                wb = Workbook()
                ws = wb.active
                ws.title = "Despesas"
                ws.append(["Arquivo", "Data", "Descrição", "Valor"])
                total = 0.0
                for d in despesas:
                    ws.append([d["arquivo"], d["data"], d["descricao"], d["valor"]])
                    try:
                        v_str = str(d["valor"] or "0").replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                        total += float(v_str)
                    except: pass
                ws.append([]); ws.append(["TOTAL GERAL", "", "", total])
                output = io.BytesIO()
                wb.save(output)
                excel_db_path = await storage.save_file(output.getvalue(), os.path.dirname(documentos[0].arquivo_path), f"Despesas_{uuid.uuid4().hex[:4]}.xlsx")
                doc_excel = models.DocumentoCliente(
                    nome="Despesas Consolidadas", arquivo_path=excel_db_path,
                    escritorio_id=escritorio_id, cliente_id=documentos[0].cliente_id, pasta_id=pasta_id,
                    tamanho=len(output.getvalue())
                )
                db.add(doc_excel)
                
            await db.commit()
            job_manager.update_job(job_id, status="completed", progress=100, message="Organização concluída!")
            
        except Exception as e:
            logger.exception(f"Erro no job de organização: {e}")
            job_manager.update_job(job_id, status="failed", message=str(e))

async def iniciar_organizacao_pasta(db: AsyncSession, current_user: models.Usuario, pasta_id: int, background_tasks: BackgroundTasks):
    job_id = job_manager.create_job()
    background_tasks.add_task(
        organizar_pasta_task, 
        job_id, 
        None, # db_factory não usado agora pois importamos no loop
        current_user.id, 
        current_user.escritorio_id, 
        pasta_id
    )
    return {"job_id": job_id}
