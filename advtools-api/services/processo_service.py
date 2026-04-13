from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import schemas
import models
import crud
import json
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
    numero_norm = dados_processo["numero_processo"]
    
    # Verifica duplicidade
    existente = await crud.get_processo_by_numero(db, numero_norm, escritorio_id)
    if existente:
        # Se existe, apenas atualiza
        return await atualizar_processo_datajud_service(db, existente.id, escritorio_id, usuario_id)

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

# ============================================
# MNI / PROJUDI Integration
# ============================================
from services.mni_service import (
    consultar_processo_mni,
    mapear_dados_mni_para_processo,
    extrair_partes_mni,
    extrair_movimentacoes_mni,
    extrair_assuntos_mni,
    analisar_processo_com_ia,
    suporta_mni,
)

async def buscar_e_criar_mni_service(db: AsyncSession, request: schemas.MNIBuscaRequest, escritorio_id: int, usuario_id: int):
    """Importa processo do PROJUDI via MNI/SOAP."""
    resultado = consultar_processo_mni(request.numero_processo)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=400, detail=resultado.get("erro", "Erro na consulta MNI."))

    # Mapear para nosso modelo
    dados_processo = mapear_dados_mni_para_processo(resultado)
    numero_norm = dados_processo["numero_processo"]

    # Verifica duplicidade
    existente = await crud.get_processo_by_numero(db, numero_norm, escritorio_id)
    if existente:
        # Se existe, apenas atualiza
        return await atualizar_processo_mni_service(db, existente.id, escritorio_id, usuario_id)

    dados_processo["cliente_id"] = request.cliente_id
    dados_processo["advogado_responsavel_id"] = usuario_id

    # Criar processo
    processo_in = schemas.ProcessoCreate(**dados_processo)
    db_processo = await crud.create_processo(db, processo_in, escritorio_id)

    # Importar Partes
    partes = extrair_partes_mni(resultado)
    for parte in partes:
        parte_in = schemas.ProcessoParteCreate(**parte)
        await crud.create_processo_parte(db, db_processo.id, parte_in)

    # Importar Assuntos
    assuntos = extrair_assuntos_mni(resultado)
    for ass in assuntos:
        ass_in = schemas.ProcessoAssuntoCreate(**ass)
        await crud.create_processo_assunto(db, db_processo.id, ass_in)

    # Importar Movimentações
    movs = extrair_movimentacoes_mni(resultado)
    for mov in movs:
        try:
            dt = datetime.fromisoformat(mov["data_hora"]) if mov["data_hora"] else datetime.now()
        except Exception:
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


async def atualizar_processo_mni_service(db: AsyncSession, processo_id: int, escritorio_id: int, usuario_id: int):
    """Atualiza movimentações de um processo existente via MNI."""
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo or not processo.numero_processo:
        raise HTTPException(status_code=400, detail="Processo sem número CNJ para consulta.")

    resultado = consultar_processo_mni(processo.numero_processo)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=400, detail=resultado.get("erro", "Erro na consulta MNI."))

    # Update metadados do processo
    cab = resultado["cabecalho"]
    status = cab.get("ProcessoStatus")
    if status:
        status_map = {"ARQUIVADO": "Arquivado", "ATIVO": "Ativo", "SUSPENSO": "Suspenso"}
        processo.status = status_map.get(status.upper(), status)
    if cab.get("ProcessoFase"):
        processo.fase_processual = cab["ProcessoFase"]
    if cab.get("valorCausa"):
        processo.valor_causa = float(cab["valorCausa"])
    db.add(processo)

    # Importar novas movimentações (idempotente)
    existentes = {(m.codigo_movimento, m.data_hora) for m in processo.movimentacoes}

    movs = extrair_movimentacoes_mni(resultado)
    novas = 0
    for mov in movs:
        try:
            dt = datetime.fromisoformat(mov["data_hora"]) if mov["data_hora"] else datetime.now()
        except Exception:
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
            novas += 1

    await db.commit()
    return await crud.get_processo(db, processo.id, escritorio_id)


async def analisar_processo_ia_service(db: AsyncSession, processo_id: int, escritorio_id: int):
    """Gera análise inteligente de prazos e tarefas via Gemini AI."""
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado.")

    # Buscar chave Gemini (banco > .env)
    escritorio = await crud.get_escritorio(db, escritorio_id)
    # Prioriza a chave do banco. Se não houver, usa Config para fallback sanitizado.
    api_key = Config.get_gemini_api_key(escritorio.gemini_api_key if escritorio else None)

    if not api_key:
        raise HTTPException(status_code=400, detail="Chave do Gemini não configurada. Configure nas Configurações do Escritório.")

    # Tenta buscar dados MNI frescos se for TJGO
    mni_data = None
    if processo.numero_processo and suporta_mni(processo.numero_processo):
        resultado = consultar_processo_mni(processo.numero_processo)
        if resultado.get("sucesso"):
            mni_data = resultado

    # Chamar análise
    analise = analisar_processo_com_ia(mni_data, processo.movimentacoes, api_key)
    
    # Persistir se não houver erro
    if analise and "erro" not in analise:
        processo.analise_ia = json.dumps(analise, ensure_ascii=False)
        processo.data_analise_ia = datetime.now()
        db.add(processo)
        await db.commit()

    return analise or {"erro": "Falha na análise IA."}

