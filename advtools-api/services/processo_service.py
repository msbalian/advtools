from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import schemas
import models
import crud
import json
from config import Config
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
    listar_processos_advogado_mni,
)
import time


async def importar_massa_projudi_service(db: AsyncSession, escritorio_id: int, usuario_id: int):
    """
    Importa em massa todos os processos com avisos pendentes do PROJUDI.
    Identifica clientes por pólo processual, faz upsert idempotente e retorna relatório.
    """
    # Buscar OAB do advogado logado
    from sqlalchemy import select
    result = await db.execute(select(models.Usuario).where(models.Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if not usuario or not usuario.oab_numero:
        raise HTTPException(status_code=400, detail="Cadastre seu número de OAB nas Configurações > Equipe antes de importar.")

    oab_advogado = usuario.oab_numero.strip()
    oab_uf = (usuario.oab_uf or "").strip().upper()

    # 1. Listar processos via avisos pendentes
    lista = listar_processos_advogado_mni()
    if not lista.get("sucesso"):
        raise HTTPException(status_code=400, detail=lista.get("erro", "Falha ao consultar PROJUDI."))

    numeros = lista["numeros"]
    if not numeros:
        return schemas.ImportacaoRelatorio(total_avisos=lista["total_avisos"])

    relatorio = schemas.ImportacaoRelatorio(total_avisos=lista["total_avisos"])

    for numero in numeros:
        try:
            # Rate limiting: 500ms entre chamadas
            time.sleep(0.5)

            # 2. Consultar processo completo
            mni_data = consultar_processo_mni(numero)
            if not mni_data.get("sucesso"):
                relatorio.erros.append(f"Processo {numero}: {mni_data.get('erro', 'Erro desconhecido')}")
                continue

            dados_processo = mapear_dados_mni_para_processo(mni_data)
            numero_norm = dados_processo["numero_processo"]

            # 3. Idempotência: verificar se já existe
            existente = await crud.get_processo_by_numero(db, numero_norm, escritorio_id)

            # 4. Identificar cliente pelo pólo do advogado
            cliente_id = await _identificar_cliente_por_polo(
                db, mni_data, oab_advogado, oab_uf, escritorio_id, relatorio
            )

            if existente:
                # UPDATE: atualizar metadados e movimentações
                await _atualizar_processo_existente(db, existente, mni_data, usuario_id)
                if cliente_id and not existente.cliente_id:
                    existente.cliente_id = cliente_id
                    db.add(existente)
                relatorio.processos_atualizados += 1
            else:
                # CREATE: novo processo
                dados_processo["cliente_id"] = cliente_id
                dados_processo["advogado_responsavel_id"] = usuario_id
                dados_processo["origem"] = "PROJUDI"

                processo_in = schemas.ProcessoCreate(**dados_processo)
                db_processo = await crud.create_processo(db, processo_in, escritorio_id)

                # Setar origem e projudi_id
                db_processo.origem = "PROJUDI"
                cab = mni_data.get("cabecalho", {})
                db_processo.projudi_id = cab.get("IdProcesso")
                db.add(db_processo)

                # Importar partes, assuntos, movimentações
                await _importar_dados_complementares(db, db_processo.id, mni_data, usuario_id)
                relatorio.processos_novos += 1

            await db.commit()

        except Exception as e:
            await db.rollback()
            relatorio.erros.append(f"Processo {numero}: {str(e)}")

    return relatorio


async def _identificar_cliente_por_polo(db, mni_data, oab_advogado, oab_uf, escritorio_id, relatorio=None):
    """Identifica o cliente no mesmo pólo do advogado e faz match/criação no banco."""
    partes = mni_data.get("cabecalho", {}).get("partes", [])
    polo_advogado = None

    # Normalizar OAB do advogado para comparação (remover tudo que não é letra/número)
    oab_clean = "".join(filter(str.isalnum, oab_advogado)).upper()

    # Encontrar o pólo do advogado pela OAB
    for parte in partes:
        for adv in parte.get("advogados", []):
            inscricao = adv.get("inscricao", "").strip().upper()
            insc_clean = "".join(filter(str.isalnum, inscricao)).upper()
            
            # Comparar (Ex: Dra Nubia tem "47259A" no perfil e Projudi tem "47259A" ou "GO47259A")
            if oab_clean in insc_clean or insc_clean in oab_clean:
                polo_advogado = parte.get("polo")
                break
        if polo_advogado:
            break

    if not polo_advogado:
        return None

    # Encontrar a primeira pessoa do mesmo pólo que NÃO é advogado
    for parte in partes:
        if parte.get("polo") == polo_advogado:
            # Esta é uma parte (não advogado) do mesmo pólo = potencial cliente
            nome_parte = parte.get("nome", "").strip()
            doc_parte = parte.get("documento", "").strip()
            if not nome_parte:
                continue

            # Match por CPF/CNPJ no banco
            if doc_parte:
                from sqlalchemy import select
                result = await db.execute(
                    select(models.Cliente).where(
                        models.Cliente.escritorio_id == escritorio_id,
                        models.Cliente.documento == doc_parte
                    )
                )
                cliente_existente = result.scalar_one_or_none()

                if cliente_existente:
                    # Verificar merge: CPF bate mas nome diferente
                    if relatorio and cliente_existente.nome.strip().upper() != nome_parte.upper():
                        relatorio.merges_sugeridos.append(schemas.ImportacaoMerge(
                            nome_banco=cliente_existente.nome,
                            nome_projudi=nome_parte,
                            cpf_cnpj=doc_parte,
                            cliente_id=cliente_existente.id
                        ))
                    if relatorio: relatorio.clientes_vinculados += 1
                    return cliente_existente.id

            # Cliente não existe → cadastrar
            tipo_pessoa = parte.get("tipo_pessoa", "Física")
            novo_cliente = models.Cliente(
                escritorio_id=escritorio_id,
                nome=nome_parte,
                documento=doc_parte if doc_parte else None,
            )
            db.add(novo_cliente)
            await db.flush()
            if relatorio: relatorio.clientes_criados += 1
            return novo_cliente.id

    return None


async def _atualizar_processo_existente(db, processo, mni_data, usuario_id):
    """Atualiza metadados e movimentações de um processo existente."""
    cab = mni_data["cabecalho"]
    status = cab.get("ProcessoStatus")
    if status:
        status_map = {"ARQUIVADO": "Arquivado", "ATIVO": "Ativo", "SUSPENSO": "Suspenso"}
        processo.status = status_map.get(status.upper(), status)
    if cab.get("ProcessoFase"):
        processo.fase_processual = cab["ProcessoFase"]
    if cab.get("valorCausa"):
        processo.valor_causa = float(cab["valorCausa"])
    if not processo.origem or processo.origem == "Manual":
        processo.origem = "PROJUDI"
    if cab.get("IdProcesso") and not processo.projudi_id:
        processo.projudi_id = cab["IdProcesso"]
    db.add(processo)

    # Importar novas movimentações (idempotente) sem lazy loading
    from sqlalchemy import select
    res_movs = await db.execute(select(models.Movimentacao).where(models.Movimentacao.processo_id == processo.id))
    movimentacoes_bd = res_movs.scalars().all()
    
    existentes = {(m.codigo_movimento, m.data_hora) for m in movimentacoes_bd}
    movs = extrair_movimentacoes_mni(mni_data)
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


async def _importar_dados_complementares(db, processo_id, mni_data, usuario_id):
    """Importa partes, assuntos e movimentações de um processo recém-criado."""
    # Partes
    partes = extrair_partes_mni(mni_data)
    for parte in partes:
        parte_in = schemas.ProcessoParteCreate(**parte)
        await crud.create_processo_parte(db, processo_id, parte_in)

    # Assuntos
    assuntos = extrair_assuntos_mni(mni_data)
    for ass in assuntos:
        ass_in = schemas.ProcessoAssuntoCreate(**ass)
        await crud.create_processo_assunto(db, processo_id, ass_in)

    # Movimentações
    movs = extrair_movimentacoes_mni(mni_data)
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
        await crud.create_movimentacao(db, processo_id, mov_in)

async def buscar_e_criar_mni_service(db: AsyncSession, request: schemas.MNIBuscaRequest, escritorio_id: int, usuario_id: int):
    """Importa processo do PROJUDI via MNI/SOAP com inteligência unificada."""
    resultado = consultar_processo_mni(request.numero_processo)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=400, detail=resultado.get("erro", "Erro na consulta MNI."))

    # Mapear para nosso modelo
    dados_processo = mapear_dados_mni_para_processo(resultado)
    numero_norm = dados_processo["numero_processo"]

    # Verifica duplicidade
    existente = await crud.get_processo_by_numero(db, numero_norm, escritorio_id)
    if existente:
        # Se existe, atualiza de forma inteligente
        return await atualizar_processo_mni_service(db, existente.id, escritorio_id, usuario_id)

    # Buscar OAB para matching de cliente
    from sqlalchemy import select
    res_user = await db.execute(select(models.Usuario).where(models.Usuario.id == usuario_id))
    usuario = res_user.scalar_one_or_none()
    
    cliente_id = request.cliente_id
    if not cliente_id and usuario and usuario.oab_numero:
        cliente_id = await _identificar_cliente_por_polo(
            db, resultado, usuario.oab_numero, usuario.oab_uf, escritorio_id, None
        )

    dados_processo["cliente_id"] = cliente_id
    dados_processo["advogado_responsavel_id"] = usuario_id
    dados_processo["origem"] = "PROJUDI"

    # Criar processo
    processo_in = schemas.ProcessoCreate(**dados_processo)
    db_processo = await crud.create_processo(db, processo_in, escritorio_id)

    # Injetar metadados específicos do PROJUDI
    cab = resultado.get("cabecalho", {})
    db_processo.origem = "PROJUDI"
    db_processo.projudi_id = cab.get("IdProcesso")
    db.add(db_processo)

    # Importar Partes, Assuntos e Movimentações (Centralizado)
    await _importar_dados_complementares(db, db_processo.id, resultado, usuario_id)
    
    await db.commit()
    return await crud.get_processo(db, db_processo.id, escritorio_id)


async def atualizar_processo_mni_service(db: AsyncSession, processo_id: int, escritorio_id: int, usuario_id: int):
    """Atualiza metadados e movimentações de forma inteligente via MNI."""
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo or not processo.numero_processo:
        raise HTTPException(status_code=400, detail="Processo não encontrado ou sem número CNJ.")

    resultado = consultar_processo_mni(processo.numero_processo)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=400, detail=resultado.get("erro", "Erro na consulta MNI."))

    # 1. Atualizar Capa e Metadados (Centralizado)
    await _atualizar_processo_existente(db, processo, resultado, usuario_id)

    # 2. Se estiver sem cliente, tentar matching por OAB
    if not processo.cliente_id:
        from sqlalchemy import select
        res_user = await db.execute(select(models.Usuario).where(models.Usuario.id == usuario_id))
        usuario = res_user.scalar_one_or_none()
        
        if usuario and usuario.oab_numero:
            cliente_id = await _identificar_cliente_por_polo(
                db, resultado, usuario.oab_numero, usuario.oab_uf, escritorio_id, None
            )
            if cliente_id:
                processo.cliente_id = cliente_id
                db.add(processo)

    await db.commit()
    return await crud.get_processo(db, processo.id, escritorio_id)


async def analisar_processo_ia_service(db: AsyncSession, processo_id: int, escritorio_id: int, usuario_id: int):
    """Gera análise inteligente de prazos e tarefas via Gemini AI."""
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado.")

    # Buscar chave Gemini (banco > .env)
    escritorio = await crud.get_escritorio(db, escritorio_id)
    api_key = Config.get_gemini_api_key(escritorio.gemini_api_key if escritorio else None)

    if not api_key:
        raise HTTPException(status_code=400, detail="Chave do Gemini não configurada.")

    # Consultar MNI se suportado
    mni_data = None
    if processo.numero_processo and suporta_mni(processo.numero_processo):
        resultado = consultar_processo_mni(processo.numero_processo)
        if resultado.get("sucesso"):
            mni_data = resultado

    # Chamar análise
    analise = analisar_processo_com_ia(mni_data, processo.movimentacoes, api_key)
    
    if analise and "erro" not in analise:
        processo.analise_ia = json.dumps(analise, ensure_ascii=False)
        processo.data_analise_ia = datetime.now()
        db.add(processo)
        
        # Gerar tarefas automaticamente
        await _criar_tarefas_do_json_analise(db, processo, analise, escritorio_id, usuario_id)
        await db.commit()

    return analise or {"erro": "Falha na análise IA."}

async def gerar_tarefas_ia_existente_service(db: AsyncSession, processo_id: int, escritorio_id: int, usuario_id: int):
    """Gera tarefas a partir de uma análise já salva no banco de dados."""
    processo = await crud.get_processo(db, processo_id, escritorio_id)
    if not processo or not processo.analise_ia:
        raise HTTPException(status_code=400, detail="Nenhuma análise IA encontrada para este processo.")

    try:
        analise = json.loads(processo.analise_ia)
        await _criar_tarefas_do_json_analise(db, processo, analise, escritorio_id, usuario_id)
        await db.commit()
        return {"sucesso": True, "mensagem": "Tarefas geradas com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar análise salva: {str(e)}")

async def _criar_tarefas_do_json_analise(db: AsyncSession, processo, analise, escritorio_id, usuario_id):
    """Helper interno para extrair tarefas do JSON e persistir no banco."""
    from services.tarefa_service import create_tarefa_service, get_tarefas_service
    import schemas
    
    tarefas_sugeridas = analise.get("tarefasPendentes", [])
    if not tarefas_sugeridas:
        return

    # Buscar tarefas atuais para evitar duplicatas (mesmo título parcial)
    tarefas_atuais = await get_tarefas_service(db, escritorio_id, processo_id=processo.id)
    titulos_existentes = [t.titulo.lower() for t in tarefas_atuais]

    import re
    from datetime import datetime

    for t_sug in tarefas_sugeridas:
        titulo = f"[IA] {t_sug.get('acao', 'Tarefa Sugerida')}"
        if titulo.lower() in titulos_existentes:
            continue # Pula se já existir

        # Parsing de Data Robusto (Regex + Múltiplos Formatos)
        vencimento = None
        raw_date = t_sug.get("prazoDataFim")
        
        if raw_date and isinstance(raw_date, str):
            # Tentar extrair data no formato DD/MM/YYYY de dentro da string (caso a IA mande texto junto)
            match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', raw_date)
            if match:
                d, m, y = match.groups()
                # Normalizar ano se vier com 2 dígitos
                if len(y) == 2: y = f"20{y}"
                try:
                    vencimento = datetime(int(y), int(m), int(d))
                except: pass
            
            # Se falhou, tentar formatos padrão ISO se a IA mandar direto
            if not vencimento:
                formats = ["%d/%m/%Y", "%Y-%m-%d"]
                for fmt in formats:
                    try:
                        vencimento = datetime.strptime(raw_date.strip(), fmt)
                        break
                    except: continue
        
        # Montar schema
        t_create = schemas.TarefaCreate(
            titulo=titulo,
            descricao=f"Sugestão automática da IA.\nUrgência: {t_sug.get('urgencia', 'Normal')}",
            status="Sugestão (IA)",
            prioridade=t_sug.get("urgencia", "Normal") if t_sug.get("urgencia") in ["Baixa", "Normal", "Alta", "Urgente"] else "Normal",
            data_vencimento=vencimento,
            processo_id=processo.id,
            cliente_id=processo.cliente_id,
            responsavel_id=processo.advogado_responsavel_id
        )
        
        try:
            await create_tarefa_service(db, t_create, escritorio_id, usuario_id)
        except Exception as e:
            print(f"Erro ao criar tarefa automática: {e}")

