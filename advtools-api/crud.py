from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
import models
import schemas
from auth import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.email == email))
    return result.scalars().first()

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
    result = await db.execute(select(models.Servico).filter(models.Servico.escritorio_id == escritorio_id))
    return result.scalars().all()

async def get_servicos_by_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(select(models.Servico).filter(
        models.Servico.cliente_id == cliente_id,
        models.Servico.escritorio_id == escritorio_id
    ))
    return result.scalars().all()

async def create_servico(db: AsyncSession, servico: schemas.ServicoCreate, escritorio_id: int):
    db_servico = models.Servico(**servico.dict(), escritorio_id=escritorio_id)
    db.add(db_servico)
    await db.commit()
    await db.refresh(db_servico)
    return db_servico

async def get_servico(db: AsyncSession, servico_id: int, escritorio_id: int):
    result = await db.execute(select(models.Servico).filter(
        models.Servico.id == servico_id,
        models.Servico.escritorio_id == escritorio_id
    ))
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
    return db_servico

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
# DOCUMENTOS DO CLIENTE
# ==========================
async def get_documentos_cliente(db: AsyncSession, cliente_id: int, escritorio_id: int):
    result = await db.execute(
        select(models.DocumentoCliente)
        .options(selectinload(models.DocumentoCliente.signatarios))
        .filter(
            models.DocumentoCliente.cliente_id == cliente_id,
            models.DocumentoCliente.escritorio_id == escritorio_id
        )
    )
    return result.scalars().all()

async def create_documento_cliente(db: AsyncSession, documento: schemas.DocumentoClienteCreate, arquivo_path: str, escritorio_id: int):
    db_doc = models.DocumentoCliente(
        escritorio_id=escritorio_id,
        cliente_id=documento.cliente_id,
        nome=documento.nome,
        arquivo_path=arquivo_path
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
