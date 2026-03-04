from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import schemas
import models
import crud
from services.datajud_service import (
    consultar_processo_datajud,
    mapear_dados_datajud_para_processo,
    extrair_movimentacoes,
    extrair_assuntos
)

async def get_processos_service(db: AsyncSession, escritorio_id: int):
    return await crud.get_processos(db, escritorio_id=escritorio_id)

async def get_processos_by_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    return await crud.get_processos_by_cliente(db, cliente_id=cliente_id, escritorio_id=escritorio_id)

async def get_processos_by_cliente_service(db: AsyncSession, cliente_id: int, escritorio_id: int):
    return await crud.get_processos_by_cliente(db, cliente_id=cliente_id, escritorio_id=escritorio_id)

async def get_processo_service(db: AsyncSession, processo_id: int, escritorio_id: int):
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo

async def create_processo_service(db: AsyncSession, processo: schemas.ProcessoCreate, escritorio_id: int):
    return await crud.create_processo(db, processo, escritorio_id)

async def update_processo_service(db: AsyncSession, processo_id: int, processo_update: schemas.ProcessoUpdate, escritorio_id: int):
    processo = await crud.update_processo(db, processo_id, processo_update, escritorio_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return processo

async def delete_processo_service(db: AsyncSession, processo_id: int, escritorio_id: int):
    success = await crud.delete_processo(db, processo_id, escritorio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return success

async def buscar_e_criar_datajud_service(db: AsyncSession, request: schemas.DataJudBuscaRequest, escritorio_id: int, usuario_id: int):
    # Consulta DataJud
    resultado = consultar_processo_datajud(request.numero_cnj, request.tribunal)
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["erro"])
    
    proc_data = resultado["data"]
    tribunal = resultado["tribunal"]
    
    # Mapeia para o nosso modelo
    dados_processo = mapear_dados_datajud_para_processo(proc_data, tribunal)
    dados_processo["cliente_id"] = request.cliente_id
    dados_processo["advogado_responsavel_id"] = usuario_id
    
    # Cria o processo
    processo_in = schemas.ProcessoCreate(**dados_processo)
    db_processo = await crud.create_processo(db, processo_in, escritorio_id)
    
    # Importa Assuntos
    assuntos = extrair_assuntos(proc_data)
    for ass in assuntos:
        ass_in = schemas.ProcessoAssuntoCreate(**ass)
        await crud.create_processo_assunto(db, db_processo.id, ass_in)
    
    # Importa Movimentações
    movs = extrair_movimentacoes(proc_data)
    for mov in movs:
        try:
            dt = datetime.fromisoformat(mov["data_hora"].replace('Z', '+00:00'))
        except:
            dt = datetime.now()
            
        mov_in = schemas.MovimentacaoCreate(
            tipo=mov["tipo"],
            codigo_movimento=mov["codigo_movimento"],
            nome_movimento=mov["nome_movimento"],
            complementos_json=mov["complementos_json"],
            data_hora=dt,
            registrado_por_id=usuario_id
        )
        await crud.create_movimentacao(db, db_processo.id, mov_in)
        
    return await crud.get_processo(db, db_processo.id, escritorio_id)

async def atualizar_processo_datajud_service(db: AsyncSession, processo_id: int, escritorio_id: int, usuario_id: int):
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo or not processo.numero_processo:
        raise HTTPException(status_code=400, detail="Processo sem número CNJ para consulta.")
    
    resultado = consultar_processo_datajud(processo.numero_processo, processo.tribunal)
    if not resultado["sucesso"]:
        raise HTTPException(status_code=400, detail=resultado["erro"])
    
    proc_data = resultado["data"]
    
    # Update Capa (Opcional - Implementar caso necessário)
    
    # Update Movimentações (Idempotente)
    existentes = {(m.codigo_movimento, m.data_hora) for m in processo.movimentacoes}
    
    novas_movs = extrair_movimentacoes(proc_data)
    for mov in novas_movs:
        try:
            dt = datetime.fromisoformat(mov["data_hora"].replace('Z', '+00:00'))
        except:
            dt = datetime.now()
            
        if (mov["codigo_movimento"], dt) not in existentes:
            mov_in = schemas.MovimentacaoCreate(
                tipo=mov["tipo"],
                codigo_movimento=mov["codigo_movimento"],
                nome_movimento=mov["nome_movimento"],
                complementos_json=mov["complementos_json"],
                data_hora=dt,
                registrado_por_id=usuario_id
            )
            await crud.create_movimentacao(db, processo.id, mov_in)
            
    return await crud.get_processo(db, processo.id, escritorio_id)
