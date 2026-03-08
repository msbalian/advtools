from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
import models
import schemas
from database import get_db
from services.auth_service import get_current_user
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/api/arquivos", tags=["Arquivos"])

@router.get("/tree")
async def get_arquivos_tree(
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna a estrutura base para a árvore de navegação lateral.
    """
    escritorio_id = current_user.escritorio_id
    
    # 1. Pastas do Escritório (Internas)
    q_pastas_internas = select(models.PastaDocumento).where(
        models.PastaDocumento.escritorio_id == escritorio_id,
        models.PastaDocumento.cliente_id == None,
        models.PastaDocumento.processo_id == None
    )
    res_internas = await db.execute(q_pastas_internas)
    pastas_internas = res_internas.scalars().all()
    
    # 2. Clientes que possuem documentos ou pastas
    q_clientes = select(models.Cliente).where(
        models.Cliente.escritorio_id == escritorio_id,
        or_(
            models.Cliente.documentos.any(),
            select(models.PastaDocumento).where(models.PastaDocumento.cliente_id == models.Cliente.id).exists()
        )
    )
    res_clientes = await db.execute(q_clientes)
    clientes_com_docs = res_clientes.scalars().all()
    
    # 3. Processos que possuem documentos ou pastas
    q_processos = select(models.Processo).where(
        models.Processo.escritorio_id == escritorio_id,
        or_(
            models.Processo.servicos.any(models.Servico.cliente_id != None), # Simplificação: se tem serviço, pode ter doc
            # Melhor: processos vinculados a pastas
            select(models.PastaDocumento).where(models.PastaDocumento.processo_id == models.Processo.id).exists()
        )
    )
    res_processos = await db.execute(q_processos)
    processos_com_docs = res_processos.scalars().all()

    return {
        "internos": pastas_internas,
        "clientes": [{"id": c.id, "nome": c.nome} for c in clientes_com_docs],
        "processos": [{"id": p.id, "numero": p.numero_processo, "titulo": p.titulo} for p in processos_com_docs]
    }

@router.get("/list")
async def list_files_global(
    tipo: str = "todos", # todos, internos, modelos, clientes, processos
    status_assinatura: Optional[str] = None,
    search: Optional[str] = None,
    current_user: models.Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listagem flat de arquivos com filtros globais.
    """
    escritorio_id = current_user.escritorio_id
    
    # Base query para documentos
    query = select(models.DocumentoCliente).options(
        selectinload(models.DocumentoCliente.cliente),
        selectinload(models.DocumentoCliente.signatarios)
    ).where(models.DocumentoCliente.escritorio_id == escritorio_id)
    
    if tipo == "internos":
        query = query.where(models.DocumentoCliente.cliente_id == None)
    elif tipo == "clientes":
        query = query.where(models.DocumentoCliente.cliente_id != None)
    # Adicionar lógica de processos se necessário (hoje docs de processos ficam na pasta do cliente/processo)
    
    if status_assinatura:
        query = query.where(models.DocumentoCliente.status_assinatura == status_assinatura)
        
    if search:
        query = query.where(models.DocumentoCliente.nome.ilike(f"%{search}%"))
        
    res = await db.execute(query)
    docs = res.scalars().all()
    
    # Adicionar modelos se o tipo for "modelos" ou "todos"
    modelos_data = []
    if tipo in ["modelos", "todos"]:
        q_modelos = select(models.ModeloDocumento).where(models.ModeloDocumento.escritorio_id == escritorio_id)
        if search:
            q_modelos = q_modelos.where(models.ModeloDocumento.nome.ilike(f"%{search}%"))
        res_mod = await db.execute(q_modelos)
        modelos = res_mod.scalars().all()
        modelos_data = [{
            "id": f"mod_{m.id}",
            "db_id": m.id,
            "nome": m.nome,
            "tipo": "Modelo",
            "arquivo_path": m.arquivo_path,
            "data_criacao": m.data_criacao,
            "is_modelo": True
        } for m in modelos]

    docs_data = [{
        "id": d.id,
        "nome": d.nome,
        "tipo": "Documento",
        "cliente": d.cliente.nome if d.cliente else "Escritório",
        "status_assinatura": d.status_assinatura,
        "data_criacao": d.data_criacao,
        "arquivo_path": d.arquivo_path,
        "is_modelo": False
    } for d in docs]
    
    return sorted(docs_data + modelos_data, key=lambda x: x["data_criacao"], reverse=True)
