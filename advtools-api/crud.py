import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct, exists
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException
import models
import schemas
from auth import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.email == email))
    return result.scalars().first()

async def check_any_superadmin_exists(db: AsyncSession) -> bool:
    result = await db.execute(select(models.Usuario).filter(models.Usuario.is_admin == True).limit(1))
    return result.scalars().first() is not None

async def ensure_default_office(db: AsyncSession):
    result = await db.execute(select(models.Escritorio).limit(1))
    esc = result.scalars().first()
    if not esc:
        esc = models.Escritorio(nome="Escritório Master", documento="000.000.000-00")
        db.add(esc)
        await db.commit()
        await db.refresh(esc)
    return esc

async def create_user(db: AsyncSession, user: schemas.UsuarioCreate):
    hashed_password = get_password_hash(user.senha)
    db_user = models.Usuario(
        email=user.email,
        senha_hash=hashed_password,
        nome=user.nome,
        escritorio_id=user.escritorio_id,
        tipo=user.tipo,
        perfil=user.perfil,
        cpf=user.cpf,
        is_admin=user.is_admin,
        ativo=user.ativo
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_usuarios(db: AsyncSession, escritorio_id: int):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.escritorio_id == escritorio_id))
    return result.scalars().all()

async def get_usuario_by_id(db: AsyncSession, user_id: int, escritorio_id: int):
    result = await db.execute(select(models.Usuario).filter(
        models.Usuario.id == user_id, 
        models.Usuario.escritorio_id == escritorio_id
    ))
    return result.scalars().first()

async def update_usuario(db: AsyncSession, user_id: int, escritorio_id: int, user_update: schemas.UsuarioUpdate):
    db_user = await get_usuario_by_id(db, user_id, escritorio_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    if "senha" in update_data and update_data["senha"]:
        update_data["senha_hash"] = get_password_hash(update_data.pop("senha"))
    elif "senha" in update_data:
        update_data.pop("senha") # Handle empty string or None without hashing
        
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_usuario(db: AsyncSession, user_id: int, escritorio_id: int):
    db_user = await get_usuario_by_id(db, user_id, escritorio_id)
    if not db_user:
        return False
        
    await db.delete(db_user)
    await db.commit()
    return True

async def get_offices(db: AsyncSession):
    result = await db.execute(select(models.Escritorio))
    return result.scalars().all()

async def create_office(db: AsyncSession, office: schemas.EscritorioCreate):
    db_office = models.Escritorio(nome=office.nome, documento=office.documento)
    db.add(db_office)
    await db.commit()
    await db.refresh(db_office)
    return db_office

async def get_escritorio(db: AsyncSession, escritorio_id: int):
    result = await db.execute(select(models.Escritorio).filter(models.Escritorio.id == escritorio_id))
    return result.scalars().first()

async def update_escritorio(db: AsyncSession, escritorio_id: int, escritorio_in: schemas.EscritorioUpdate):
    db_esc = await get_escritorio(db, escritorio_id)
    if not db_esc:
        return None
        
    update_data = escritorio_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_esc, key, value)
        
    db.add(db_esc)
    await db.commit()
    await db.refresh(db_esc)
    return db_esc

# ==========================
# CRUD Cliente
# ==========================
async def get_clientes(db: AsyncSession, escritorio_id: int):
    result = await db.execute(select(models.Cliente).filter(models.Cliente.escritorio_id == escritorio_id))
    return result.scalars().all()

async def get_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(select(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.escritorio_id == escritorio_id
    ))
    return result.scalars().first()

async def create_cliente(db: AsyncSession, cliente: schemas.ClienteCreate, escritorio_id: int):
    db_cliente = models.Cliente(**cliente.dict(), escritorio_id=escritorio_id)
    db.add(db_cliente)
    await db.commit()
    await db.refresh(db_cliente)
    return db_cliente

async def update_cliente(db: AsyncSession, cliente_id: int, cliente: schemas.ClienteUpdate, escritorio_id: int):
    db_cliente = await get_cliente(db, cliente_id, escritorio_id)
    if not db_cliente:
        return None
    
    update_data = cliente.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)
        
    db.add(db_cliente)
    await db.commit()
    await db.refresh(db_cliente)
    return db_cliente

async def delete_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    db_cliente = await get_cliente(db, cliente_id, escritorio_id)
    if not db_cliente:
        return False
    
    await db.delete(db_cliente)
    await db.commit()
    return True

# ==========================
# CRUD Servico
# ==========================
async def get_servicos(db: AsyncSession, escritorio_id: int):
    result = await db.execute(
        select(models.Servico)
        .options(selectinload(models.Servico.tipo_servico))
        .filter(models.Servico.escritorio_id == escritorio_id)
    )
    return result.scalars().all()

async def get_servicos_by_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.Servico)
        .options(selectinload(models.Servico.tipo_servico))
        .filter(
            models.Servico.cliente_id == cliente_id,
            models.Servico.escritorio_id == escritorio_id
        )
    )
    return result.scalars().all()

async def create_servico(db: AsyncSession, servico: schemas.ServicoCreate, escritorio_id: int):
    db_servico = models.Servico(**servico.dict(), escritorio_id=escritorio_id)
    db.add(db_servico)
    await db.commit()
    await db.refresh(db_servico)
    
    # Sincroniza pagamentos com a tabela de transações
    await sincronizar_pagamentos_servico(db, db_servico)
    
    return await get_servico(db, db_servico.id, escritorio_id)

async def sincronizar_pagamentos_servico(db: AsyncSession, servico: models.Servico):
    if not servico.condicoes_pagamento:
        return
        
    try:
        pagamentos = json.loads(servico.condicoes_pagamento)
        if not isinstance(pagamentos, list):
            return
            
        # Para simplificar na automação, removemos as transações pendentes/atrasadas vinculadas ao serviço 
        # e as recriamos com base no novo JSON. Se já estiver 'Pago', mantemos.
        from sqlalchemy import delete
        await db.execute(
            delete(models.Transacao).where(
                models.Transacao.servico_id == servico.id,
                models.Transacao.status.in_(['Pendente', 'Atrasado'])
            )
        )
        
        for p in pagamentos:
            valor = float(p.get('valor') or 0)
            data_str = p.get('data')
            if not valor or not data_str:
                continue
                
            try:
                data_vencimento = datetime.strptime(data_str, "%d/%m/%Y")
            except ValueError:
                continue
            
            nova_transacao = models.Transacao(
                escritorio_id=servico.escritorio_id,
                cliente_id=servico.cliente_id,
                servico_id=servico.id,
                tipo="Receita",
                categoria="Honorários",
                valor=valor,
                descricao=f"Parcela de serviço: {servico.descricao or 'Serviço'}",
                status="Pendente",
                data_vencimento=data_vencimento
            )
            db.add(nova_transacao)
        
        await db.commit()
    except Exception as e:
        print(f"Erro ao sincronizar pagamentos do serviço {servico.id}: {e}")

async def get_servico(db: AsyncSession, servico_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.Servico)
        .options(selectinload(models.Servico.tipo_servico))
        .filter(
            models.Servico.id == servico_id,
            models.Servico.escritorio_id == escritorio_id
        )
    )
    return result.scalars().first()

async def update_servico(db: AsyncSession, servico_id: int, servico: schemas.ServicoUpdate, escritorio_id: int):
    db_servico = await get_servico(db, servico_id, escritorio_id)
    if not db_servico:
        return None
    
    update_data = servico.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_servico, key, value)
        
    db.add(db_servico)
    await db.commit()
    await db.refresh(db_servico)
    
    # Sincroniza pagamentos se as condições mudaram
    if "condicoes_pagamento" in update_data:
        await sincronizar_pagamentos_servico(db, db_servico)
        
    return await get_servico(db, db_servico.id, escritorio_id)

async def delete_servico(db: AsyncSession, servico_id: int, escritorio_id: int):
    db_servico = await get_servico(db, servico_id, escritorio_id)
    if not db_servico:
        return False
    
    await db.delete(db_servico)
    await db.commit()
    return True

# ==========================
# PARTES ENVOLVIDAS
# ==========================
async def get_partes_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(select(models.ParteEnvolvida).filter(
        models.ParteEnvolvida.cliente_id == cliente_id,
        models.ParteEnvolvida.escritorio_id == escritorio_id
    ))
    return result.scalars().all()

async def create_parte_envolvida(db: AsyncSession, parte: schemas.ParteEnvolvidaCreate):
    db_parte = models.ParteEnvolvida(**parte.dict())
    db.add(db_parte)
    await db.commit()
    await db.refresh(db_parte)
    return db_parte

async def update_parte_envolvida(db: AsyncSession, parte_id: int, escritorio_id: int, parte_update: schemas.ParteEnvolvidaUpdate):
    result = await db.execute(select(models.ParteEnvolvida).filter(
        models.ParteEnvolvida.id == parte_id,
        models.ParteEnvolvida.escritorio_id == escritorio_id
    ))
    db_parte = result.scalars().first()
    if not db_parte:
        return None
    
    update_data = parte_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_parte, key, value)
        
    db.add(db_parte)
    await db.commit()
    await db.refresh(db_parte)
    return db_parte

async def delete_parte_envolvida(db: AsyncSession, parte_id: int, escritorio_id: int):
    result = await db.execute(select(models.ParteEnvolvida).filter(
        models.ParteEnvolvida.id == parte_id,
        models.ParteEnvolvida.escritorio_id == escritorio_id
    ))
    db_parte = result.scalars().first()
    if not db_parte:
        return False
    
    await db.delete(db_parte)
    await db.commit()
    return True

# ==========================
# GESTÃO DE PASTAS DE DOCUMENTOS
# ==========================
async def get_pastas(db: AsyncSession, escritorio_id: int, cliente_id: Optional[int] = None, servico_id: Optional[int] = None, parent_id: Optional[int] = -1, processo_id: Optional[int] = None):
    query = select(models.PastaDocumento).filter(models.PastaDocumento.escritorio_id == escritorio_id)
    
    if cliente_id is not None:
        if cliente_id == 0:
            query = query.filter(models.PastaDocumento.cliente_id.is_(None))
        else:
            query = query.filter(models.PastaDocumento.cliente_id == cliente_id)
    if servico_id is not None:
        query = query.filter(models.PastaDocumento.servico_id == servico_id)
    if processo_id is not None:
        query = query.filter(models.PastaDocumento.processo_id == processo_id)
    if parent_id != -1:
        # Se for None, filtramos por parent_id is null (Raiz)
        # Se for um ID, filtramos por esse ID
        query = query.filter(models.PastaDocumento.parent_id == parent_id)
        
    result = await db.execute(query)
    pastas_list = result.scalars().all()
    
    from sqlalchemy import func
    for p in pastas_list:
        sz_q = select(func.sum(models.DocumentoCliente.tamanho)).where(models.DocumentoCliente.pasta_id == p.id)
        sz_res = await db.execute(sz_q)
        p.tamanho_total = sz_res.scalar() or 0
        
    return pastas_list

async def get_pasta_by_id(db: AsyncSession, pasta_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.PastaDocumento).filter(
            models.PastaDocumento.id == pasta_id,
            models.PastaDocumento.escritorio_id == escritorio_id
        )
    )
    return result.scalars().first()

async def create_pasta(db: AsyncSession, pasta: schemas.PastaDocumentoCreate, escritorio_id: int):
    pasta_data = pasta.dict()
    if pasta_data.get('parent_id') == -1:
        pasta_data['parent_id'] = None
        
    db_pasta = models.PastaDocumento(**pasta_data, escritorio_id=escritorio_id)
    db.add(db_pasta)
    await db.commit()
    await db.refresh(db_pasta)
    return db_pasta

async def update_pasta(db: AsyncSession, pasta_id: int, pasta_update: schemas.PastaDocumentoUpdate, escritorio_id: int):
    db_pasta = await get_pasta_by_id(db, pasta_id, escritorio_id)
    if not db_pasta:
        return None
    
    update_data = pasta_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pasta, key, value)
        
    db.add(db_pasta)
    await db.commit()
    await db.refresh(db_pasta)
    return db_pasta

async def delete_pasta(db: AsyncSession, pasta_id: int, escritorio_id: int):
    db_pasta = await get_pasta_by_id(db, pasta_id, escritorio_id)
    if not db_pasta:
        return False, "Pasta não encontrada."
        
    result_sub = await db.execute(select(models.PastaDocumento).filter(models.PastaDocumento.parent_id == pasta_id).limit(1))
    if result_sub.scalars().first():
        return False, "Não é possível excluir. A pasta contém subpastas."
        
    result_docs = await db.execute(select(models.DocumentoCliente).filter(models.DocumentoCliente.pasta_id == pasta_id).limit(1))
    if result_docs.scalars().first():
        return False, "Não é possível excluir. A pasta contém documentos."
    
    await db.delete(db_pasta)
    await db.commit()
    return True, "Pasta excluída com sucesso."

# ==========================
# DOCUMENTOS DO CLIENTE
# ==========================
async def get_documentos_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int, pasta_id: Optional[int] = -1):
    query = select(models.DocumentoCliente).options(selectinload(models.DocumentoCliente.signatarios)).filter(
        models.DocumentoCliente.cliente_id == cliente_id,
        models.DocumentoCliente.escritorio_id == escritorio_id
    )
    if pasta_id == -1:
        query = query.filter(models.DocumentoCliente.pasta_id == None)
    else:
        query = query.filter(models.DocumentoCliente.pasta_id == pasta_id)
        
    result = await db.execute(query)
    return result.scalars().all()

async def get_documentos_escritorio(db: AsyncSession, escritorio_id: int, pasta_id: Optional[int] = -1):
    query = select(models.DocumentoCliente).options(selectinload(models.DocumentoCliente.signatarios)).filter(
        models.DocumentoCliente.cliente_id == None,
        models.DocumentoCliente.escritorio_id == escritorio_id
    )
    if pasta_id == -1:
        query = query.filter(models.DocumentoCliente.pasta_id == None)
    else:
        query = query.filter(models.DocumentoCliente.pasta_id == pasta_id)
        
    result = await db.execute(query)
    return result.scalars().all()

async def create_documento_cliente(db: AsyncSession, documento: schemas.DocumentoClienteCreate, arquivo_path: str, escritorio_id: int, **kwargs):
    db_doc = models.DocumentoCliente(
        escritorio_id=escritorio_id,
        cliente_id=documento.cliente_id,
        pasta_id=documento.pasta_id if documento.pasta_id != -1 else None,
        nome=documento.nome,
        arquivo_path=arquivo_path,
        tamanho=kwargs.get('tamanho')
    )
    db.add(db_doc)
    await db.commit()
    # Forçamos o refresh para garantir que IDs e relacionamentos vazios (mas carregados) estejam no __dict__
    await db.refresh(db_doc, attribute_names=["signatarios"])
    return db_doc

async def get_documento_by_id(db: AsyncSession, documento_id: int, escritorio_id: int) -> Optional[models.DocumentoCliente]:
    result = await db.execute(
        select(models.DocumentoCliente)
        .options(selectinload(models.DocumentoCliente.signatarios))
        .filter(
            models.DocumentoCliente.id == documento_id,
            models.DocumentoCliente.escritorio_id == escritorio_id
        )
    )
    return result.scalars().first()

async def delete_documento_cliente(db: AsyncSession, documento_id: int, escritorio_id: int):
    db_doc = await get_documento_by_id(db, documento_id, escritorio_id)
    if not db_doc:
        return False
    
    await db.delete(db_doc)
    await db.commit()
    return db_doc # Retorna o doc deletado para poder excluir o arquivo físico no main.py

# ==========================
# GESTÃO DE ASSINATURAS (ADVtools Sign)
# ==========================
import uuid

async def get_signatarios(db: AsyncSession, documento_id: int, escritorio_id: int):
    # Garante que o documento pertence ao escritorio
    doc = await get_documento_by_id(db, documento_id, escritorio_id)
    if not doc:
        return None
        
    result = await db.execute(select(models.Signatario).filter(
        models.Signatario.documento_id == documento_id
    ))
    return result.scalars().all()

async def create_signatario(db: AsyncSession, documento_id: int, signatario: schemas.SignatarioCreate, escritorio_id: int):
    doc = await get_documento_by_id(db, documento_id, escritorio_id)
    if not doc:
        return None
        
    token = uuid.uuid4().hex
    # Inicializa token de assinatura se necessário e atualiza status para Pendente
    if not doc.token_assinatura:
        doc.token_assinatura = uuid.uuid4().hex
    doc.status_assinatura = 'Pendente'
    db.add(doc)
        
    db_sig = models.Signatario(
        documento_id=documento_id,
        token_acesso=token,
        nome=signatario.nome,
        email=signatario.email,
        cpf=signatario.cpf,
        funcao=signatario.funcao
    )
    db.add(db_sig)
    await db.commit()
    await db.refresh(db_sig)
    return db_sig

async def delete_signatario(db: AsyncSession, documento_id: int, signatario_id: int, escritorio_id: int):
    # Verifica se o documento pertence ao escritório
    doc = await get_documento_by_id(db, documento_id, escritorio_id)
    if not doc:
        return False
    
    # Busca o signatário
    result = await db.execute(select(models.Signatario).filter(
        models.Signatario.id == signatario_id,
        models.Signatario.documento_id == documento_id
    ))
    db_sig = result.scalars().first()
    
    if not db_sig:
        return False
    
    # Conta quantos signatários existem ANTES de deletar
    from sqlalchemy import func
    count_result = await db.execute(
        select(func.count()).select_from(models.Signatario).where(
            models.Signatario.documento_id == documento_id
        )
    )
    total_antes = count_result.scalar() or 0
    
    # Deleta o signatário
    await db.delete(db_sig)
    await db.commit()
    
    # Se era o último, reseta o status via SQL direto (evita conflitos de sessão ORM)
    if total_antes <= 1:
        from sqlalchemy import update as sql_update
        await db.execute(
            sql_update(models.DocumentoCliente)
            .where(models.DocumentoCliente.id == documento_id)
            .values(status_assinatura='Aguardando')
        )
        await db.commit()
    
    return True

async def update_signatario_posicao(db: AsyncSession, signatario_id: int, payload: schemas.SignatarioPosicoesUpdate):
    result = await db.execute(select(models.Signatario).filter(
        models.Signatario.id == signatario_id
    ))
    db_sig = result.scalars().first()
    
    if not db_sig:
        return False
        
    # Delete old positions
    from sqlalchemy import delete
    await db.execute(
        delete(models.SignatarioPosicao).where(models.SignatarioPosicao.signatario_id == signatario_id)
    )
    
    # Insert new positions
    new_pos_list = []
    for pos in payload.posicoes:
        nova_posicao = models.SignatarioPosicao(
            signatario_id=signatario_id,
            page_number=pos.page_number,
            x_pos=pos.x_pos,
            y_pos=pos.y_pos,
            width=pos.width,
            height=pos.height,
            docWidth=pos.docWidth,
            docHeight=pos.docHeight
        )
        new_pos_list.append(nova_posicao)
        db.add(nova_posicao)
        
    # Salva status de visualizacao no proprio modelo legados por conveniencia e evitar migration
    if len(payload.posicoes) > 0:
        db_sig.page_number = payload.posicoes[0].page_number
    
    db.add(db_sig)
    await db.commit()
    await db.refresh(db_sig)
    return db_sig
    
# Funções de Vistas Públicas (Não necessitam de `escritorio_id`, baseiam-se no token)
async def get_signatario_by_token(db: AsyncSession, token: str):
    result = await db.execute(select(models.Signatario).filter(
        models.Signatario.token_acesso == token
    ))
    return result.scalars().first()

async def get_documentacao_by_validacao(db: AsyncSession, token_validacao: str):
    result = await db.execute(select(models.DocumentoCliente).filter(
        models.DocumentoCliente.token_validacao == token_validacao
    ))
    return result.scalars().first()

# ==========================
# CRUD PROCESSOS JUDICIAIS
# ==========================

async def get_processos(db: AsyncSession, escritorio_id: int):
    result = await db.execute(
        select(models.Processo)
        .options(
            selectinload(models.Processo.partes),
            selectinload(models.Processo.assuntos),
            selectinload(models.Processo.movimentacoes),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.responsavel),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.cliente),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.processo),
            selectinload(models.Processo.pasta_trabalho),
            selectinload(models.Processo.servico).selectinload(models.Servico.tipo_servico)
        )
        .filter(models.Processo.escritorio_id == escritorio_id)
    )
    return result.scalars().all()

async def get_processos_by_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.Processo)
        .options(
            selectinload(models.Processo.partes),
            selectinload(models.Processo.assuntos),
            selectinload(models.Processo.movimentacoes),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.responsavel),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.cliente),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.processo),
            selectinload(models.Processo.pasta_trabalho),
            selectinload(models.Processo.servico).selectinload(models.Servico.tipo_servico)
        )
        .filter(
            models.Processo.cliente_id == cliente_id,
            models.Processo.escritorio_id == escritorio_id
        )
    )
    return result.scalars().all()

async def get_processo(db: AsyncSession, processo_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.Processo)
        .options(
            selectinload(models.Processo.partes),
            selectinload(models.Processo.assuntos),
            selectinload(models.Processo.movimentacoes),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.responsavel),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.cliente),
            selectinload(models.Processo.tarefas).selectinload(models.Tarefa.processo),
            selectinload(models.Processo.pasta_trabalho),
            selectinload(models.Processo.servico).selectinload(models.Servico.tipo_servico)
        )
        .filter(
            models.Processo.id == processo_id,
            models.Processo.escritorio_id == escritorio_id
        )
    )
    return result.scalars().first()

async def create_processo(db: AsyncSession, processo: schemas.ProcessoCreate, escritorio_id: int):
    db_processo = models.Processo(**processo.dict(), escritorio_id=escritorio_id)
    db.add(db_processo)
    await db.commit()
    return await get_processo(db, db_processo.id, escritorio_id)

async def update_processo(db: AsyncSession, processo_id: int, processo_update: schemas.ProcessoUpdate, escritorio_id: int):
    db_processo = await get_processo(db, processo_id, escritorio_id)
    if not db_processo:
        return None
    
    update_data = processo_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_processo, key, value)
        
    db.add(db_processo)
    await db.commit()
    return await get_processo(db, db_processo.id, escritorio_id)

async def delete_processo(db: AsyncSession, processo_id: int, escritorio_id: int):
    db_processo = await get_processo(db, processo_id, escritorio_id)
    if not db_processo:
        return False
    
    await db.delete(db_processo)
    await db.commit()
    return True

# Partes, Assuntos e Movimentações
async def create_processo_parte(db: AsyncSession, processo_id: int, parte: schemas.ProcessoParteCreate):
    db_parte = models.ProcessoParte(**parte.dict(), processo_id=processo_id)
    db.add(db_parte)
    await db.commit()
    await db.refresh(db_parte)
    return db_parte

async def create_processo_assunto(db: AsyncSession, processo_id: int, assunto: schemas.ProcessoAssuntoCreate):
    db_assunto = models.ProcessoAssunto(**assunto.dict(), processo_id=processo_id)
    db.add(db_assunto)
    await db.commit()
    await db.refresh(db_assunto)
    return db_assunto

async def create_movimentacao(db: AsyncSession, processo_id: int, movimentacao: schemas.MovimentacaoCreate):
    db_mov = models.Movimentacao(**movimentacao.dict(), processo_id=processo_id)
    db.add(db_mov)
    await db.commit()
    await db.refresh(db_mov)
    return db_mov

# ==========================
# CONFIGURAÇÕES DO ESCRITÓRIO
# ==========================

async def get_pastas_trabalho(db: AsyncSession, escritorio_id: int):
    result = await db.execute(select(models.PastaTrabalho).filter(models.PastaTrabalho.escritorio_id == escritorio_id))
    return result.scalars().all()

async def create_pasta_trabalho(db: AsyncSession, pasta: schemas.PastaTrabalhoCreate, escritorio_id: int):
    db_pasta = models.PastaTrabalho(**pasta.dict(), escritorio_id=escritorio_id)
    db.add(db_pasta)
    await db.commit()
    await db.refresh(db_pasta)
    return db_pasta

async def delete_pasta_trabalho(db: AsyncSession, pasta_id: int, escritorio_id: int):
    result = await db.execute(select(models.PastaTrabalho).filter(
        models.PastaTrabalho.id == pasta_id,
        models.PastaTrabalho.escritorio_id == escritorio_id
    ))
    db_pasta = result.scalars().first()
    if not db_pasta:
        return False
    await db.delete(db_pasta)
    await db.commit()
    return True

async def get_tipos_servico(db: AsyncSession, escritorio_id: int):
    result = await db.execute(select(models.TipoServico).filter(models.TipoServico.escritorio_id == escritorio_id))
    return result.scalars().all()

async def create_tipo_servico(db: AsyncSession, tipo: schemas.TipoServicoCreate, escritorio_id: int):
    db_tipo = models.TipoServico(**tipo.dict(), escritorio_id=escritorio_id)
    db.add(db_tipo)
    await db.commit()
    await db.refresh(db_tipo)
    return db_tipo

async def delete_tipo_servico(db: AsyncSession, tipo_id: int, escritorio_id: int):
    result = await db.execute(select(models.TipoServico).filter(
        models.TipoServico.id == tipo_id,
        models.TipoServico.escritorio_id == escritorio_id
    ))
    db_tipo = result.scalars().first()
    if not db_tipo:
        return False
    await db.delete(db_tipo)
    await db.commit()
    return True

# ==========================
# DASHBOARD / ESTATÍSTICAS
# ==========================
async def get_dashboard_stats(db: AsyncSession, escritorio_id: int):
    # 1. Processos Ativos
    res_proc = await db.execute(
        select(func.count(models.Processo.id))
        .where(models.Processo.escritorio_id == escritorio_id)
        .where(models.Processo.status == 'Ativo')
    )
    processos_ativos = res_proc.scalar() or 0

    # 2. Clientes Ativos (Total)
    res_clie = await db.execute(
        select(func.count(models.Cliente.id))
        .where(models.Cliente.escritorio_id == escritorio_id)
    )
    clientes_ativos = res_clie.scalar() or 0

    # 3. Assinaturas Pendentes (Aguardando ou Parcial) - Apenas se houver signatários
    res_ass = await db.execute(
        select(func.count(models.DocumentoCliente.id))
        .where(models.DocumentoCliente.escritorio_id == escritorio_id)
        .where(models.DocumentoCliente.status_assinatura.in_(['Aguardando', 'Parcial']))
        .where(exists().where(models.Signatario.documento_id == models.DocumentoCliente.id))
    )
    assinaturas_pendentes = res_ass.scalar() or 0

    # 4. Receita deste Mês (Somatória de condicoes_pagamento JSON)
    res_serv = await db.execute(
        select(models.Servico)
        .where(models.Servico.escritorio_id == escritorio_id)
    )
    servicos = res_serv.scalars().all()

    current_month_year = datetime.now().strftime("%m/%Y")
    receita_total = 0.0

    for s in servicos:
        if s.condicoes_pagamento:
            try:
                pagamentos = json.loads(s.condicoes_pagamento)
                if isinstance(pagamentos, list):
                    for p in pagamentos:
                        # O formato no frontend é DD/MM/AAAA
                        data_pg = p.get('data', '')
                        if data_pg and data_pg.endswith(current_month_year):
                            receita_total += float(p.get('valor') or 0)
            except (json.JSONDecodeError, ValueError):
                continue

    return {
        "processos_ativos": processos_ativos,
        "clientes_ativos": clientes_ativos,
        "assinaturas_pendentes": assinaturas_pendentes,
        "receita_mes": receita_total
    }

# ==========================
# CRUD FINANCEIRO (TRANSAÇÕES)
# ==========================
async def get_transacoes(db: AsyncSession, escritorio_id: int, mes: Optional[int] = None, ano: Optional[int] = None):
    query = select(models.Transacao).options(
        selectinload(models.Transacao.cliente),
        selectinload(models.Transacao.processo)
    ).filter(models.Transacao.escritorio_id == escritorio_id)
    
    if mes and ano:
        import datetime
        start_date = datetime.date(ano, mes, 1)
        if mes == 12:
            end_date = datetime.date(ano + 1, 1, 1)
        else:
            end_date = datetime.date(ano, mes + 1, 1)
        query = query.filter(models.Transacao.data_vencimento >= start_date, models.Transacao.data_vencimento < end_date)
    
    result = await db.execute(query.order_by(models.Transacao.data_vencimento.desc()))
    return result.scalars().all()

async def create_transacao(db: AsyncSession, transacao: schemas.TransacaoCreate, escritorio_id: int):
    db_transacao = models.Transacao(**transacao.dict(), escritorio_id=escritorio_id)
    db.add(db_transacao)
    await db.commit()
    await db.refresh(db_transacao)
    
    # Recarrega com relacionamentos para evitar MissingGreenlet na serialização
    result = await db.execute(
        select(models.Transacao)
        .options(selectinload(models.Transacao.cliente), selectinload(models.Transacao.processo))
        .filter(models.Transacao.id == db_transacao.id)
    )
    return result.scalars().first()

async def update_transacao(db: AsyncSession, transacao_id: int, transacao_update: schemas.TransacaoUpdate, escritorio_id: int):
    result = await db.execute(select(models.Transacao).filter(
        models.Transacao.id == transacao_id,
        models.Transacao.escritorio_id == escritorio_id
    ))
    db_transacao = result.scalars().first()
    if not db_transacao:
        return None
        
    update_data = transacao_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transacao, key, value)
        
    db.add(db_transacao)
    await db.commit()
    await db.refresh(db_transacao)
    
    # Recarrega com relacionamentos para evitar MissingGreenlet na serialização
    result = await db.execute(
        select(models.Transacao)
        .options(selectinload(models.Transacao.cliente), selectinload(models.Transacao.processo))
        .filter(models.Transacao.id == db_transacao.id)
    )
    return result.scalars().first()

async def delete_transacao(db: AsyncSession, transacao_id: int, escritorio_id: int):
    result = await db.execute(select(models.Transacao).filter(
        models.Transacao.id == transacao_id,
        models.Transacao.escritorio_id == escritorio_id
    ))
    db_transacao = result.scalars().first()
    if not db_transacao:
        return False
    await db.delete(db_transacao)
    await db.commit()
    return True

async def get_fluxo_caixa(db: AsyncSession, escritorio_id: int, mes: int, ano: int):
    transacoes = await get_transacoes(db, escritorio_id, mes, ano)
    
    total_receitas = sum(t.valor for t in transacoes if t.tipo == 'Receita' and t.status != 'Cancelado')
    total_despesas = sum(t.valor for t in transacoes if t.tipo == 'Despesa' and t.status != 'Cancelado')
    
    from datetime import datetime
    hoje = datetime.now()
    total_atrasado = sum(t.valor for t in transacoes if t.tipo == 'Receita' and t.status == 'Pendente' and t.data_vencimento < hoje)
    
    mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][mes-1]
    
    return {
        "mes": mes_nome,
        "ano": ano,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "total_atrasado": total_atrasado,
        "saldo": total_receitas - total_despesas,
        "transacoes": transacoes
    }
