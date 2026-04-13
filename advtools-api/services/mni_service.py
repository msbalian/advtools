"""
Serviço de integração com o WebService MNI/PROJUDI TJGO.
Consulta processos, extrai movimentações enriquecidas, partes e documentos
via SOAP, e opcionalmente analisa com Gemini AI.
"""
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

from config import Config

logger = logging.getLogger(__name__)

WSDL_URL = "https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL"

# Modelos Gemini para fallback (ordem de preferência)
GEMINI_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.0-flash-lite",
    "models/gemini-2.0-flash",
]

# Tribunais com suporte MNI (PROJUDI) configurado
TRIBUNAIS_MNI = {"TJGO"}


def _limpar_numero_cnj(numero: str) -> str:
    return numero.replace(".", "").replace("-", "").strip()


def _detectar_tribunal(numero_cnj: str) -> Optional[str]:
    """Detecta o tribunal pela posição J.TT do número CNJ."""
    limpo = _limpar_numero_cnj(numero_cnj)
    if len(limpo) != 20:
        return None
    justica = limpo[13]
    tribunal_cod = limpo[14:16]
    cod_map = {("8", "09"): "TJGO"}
    return cod_map.get((justica, tribunal_cod))


def suporta_mni(numero_cnj: str) -> bool:
    """Verifica se o número CNJ pertence a um tribunal com MNI configurado."""
    tribunal = _detectar_tribunal(numero_cnj)
    return tribunal in TRIBUNAIS_MNI


def consultar_processo_mni(numero_cnj: str) -> Dict[str, Any]:
    """Consulta processo completo via MNI/SOAP e retorna dados estruturados."""
    from zeep import Client
    from zeep.settings import Settings

    numero_limpo = _limpar_numero_cnj(numero_cnj)

    if not Config.PROJUDI_USER or not Config.PROJUDI_PASSWORD:
        return {"sucesso": False, "erro": "Credenciais do PROJUDI não configuradas (PROJUDI_USER/PASSWORD)."}

    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        client = Client(wsdl=WSDL_URL, settings=settings)

        response = client.service.consultarProcesso(
            idConsultante=Config.PROJUDI_USER,
            senhaConsultante=Config.PROJUDI_PASSWORD,
            numeroProcesso=numero_limpo,
            movimentos=True,
            incluirCabecalho=True,
            incluirDocumentos=True
        )

        if not response.sucesso:
            return {"sucesso": False, "erro": response.mensagem or "Erro na consulta MNI."}

        proc = response.processo
        dados = proc.dadosBasicos

        # ===== Cabecalho =====
        orgao = getattr(dados, 'orgaoJulgador', None)
        cabecalho = {
            "numero": getattr(dados, 'numero', ''),
            "classeProcessual": getattr(dados, 'classeProcessual', ''),
            "codigoLocalidade": getattr(dados, 'codigoLocalidade', ''),
            "valorCausa": float(getattr(dados, 'valorCausa', 0) or 0),
            "nivelSigilo": getattr(dados, 'nivelSigilo', 0),
            "orgaoJulgador": getattr(orgao, 'nomeOrgao', '') if orgao else '',
            "codigoOrgao": getattr(orgao, 'codigoOrgao', 0) if orgao else 0,
        }

        # Parametros extras (status, fase, area, magistrado)
        for p in (getattr(dados, 'outroParametro', []) or []):
            nome_p = getattr(p, 'nome', '')
            valor_p = getattr(p, 'valor', '')
            if nome_p in ('ProcessoStatus', 'ProcessoFase', 'Area', 'DataDistribuicao', 'Magistrado', 'IdProcesso'):
                cabecalho[nome_p] = valor_p

        # ===== Partes =====
        partes_resultado = []
        for polo in (getattr(dados, 'polo', []) or []):
            tipo_polo = getattr(polo, 'polo', '')
            for parte in (getattr(polo, 'parte', []) or []):
                pessoa = getattr(parte, 'pessoa', None)
                if not pessoa:
                    continue
                nome = getattr(pessoa, 'nome', '')
                documento = getattr(pessoa, 'numeroDocumentoPrincipal', '')
                tipo_pessoa = getattr(pessoa, 'tipoPessoa', '')

                advogados = []
                for adv in (getattr(parte, 'advogado', []) or []):
                    advogados.append({
                        "nome": getattr(adv, 'nome', ''),
                        "inscricao": getattr(adv, 'inscricao', ''),
                    })

                partes_resultado.append({
                    "nome": nome,
                    "documento": documento,
                    "tipo_pessoa": "Física" if tipo_pessoa == "fisica" else "Jurídica",
                    "polo": "Polo Ativo" if tipo_polo == "AT" else "Polo Passivo",
                    "advogados": advogados,
                })

        cabecalho["partes"] = partes_resultado

        # ===== Documentos (mapa para vincular às movimentações) =====
        docs_raw = getattr(proc, 'documento', []) or []
        doc_map = {}
        for doc in docs_raw:
            doc_id = str(getattr(doc, 'idDocumento', ''))
            nome_arq = ''
            tipo_arq = ''
            for p in (getattr(doc, 'outroParametro', []) or []):
                if getattr(p, 'nome', '') == 'NomeArquivo':
                    nome_arq = getattr(p, 'valor', '')
                elif getattr(p, 'nome', '') == 'ArquivoTipo':
                    tipo_arq = getattr(p, 'valor', '')
            doc_map[doc_id] = {
                "id": doc_id,
                "tipo": getattr(doc, 'tipoDocumento', ''),
                "descricao": getattr(doc, 'descricao', ''),
                "mimetype": getattr(doc, 'mimetype', ''),
                "nomeArquivo": nome_arq,
                "tipoArquivo": tipo_arq,
            }

        # ===== Movimentações =====
        movs_raw = getattr(proc, 'movimento', []) or []
        movimentacoes = []
        for mov in movs_raw:
            dt_str = str(getattr(mov, 'dataHora', ''))
            mov_nac = getattr(mov, 'movimentoNacional', None)
            cod_nac = getattr(mov_nac, 'codigoNacional', 0) if mov_nac else 0
            mov_loc = getattr(mov, 'movimentoLocal', None)
            desc_loc = getattr(mov_loc, 'descricao', '') if mov_loc else ''
            comps = getattr(mov, 'complemento', []) or []
            complemento = ' '.join([str(c) for c in comps if c]) if comps else ''

            # Documentos vinculados
            docs_vinc_ids = getattr(mov, 'idDocumentoVinculado', []) or []
            docs_vinc = [doc_map.get(str(d), {"id": str(d)}) for d in docs_vinc_ids]

            # Parse data
            dt_iso = None
            dt_formatted = ''
            if dt_str and len(dt_str) >= 8:
                try:
                    dt_obj = datetime.strptime(dt_str[:14], '%Y%m%d%H%M%S')
                    dt_iso = dt_obj.isoformat()
                    dt_formatted = dt_obj.strftime('%d/%m/%Y %H:%M')
                except Exception:
                    dt_formatted = dt_str

            movimentacoes.append({
                "data": dt_formatted,
                "dataISO": dt_iso,
                "codigoNacional": cod_nac,
                "descricao": desc_loc,
                "complemento": complemento,
                "documentos": docs_vinc if docs_vinc else None,
            })

        return {
            "sucesso": True,
            "cabecalho": cabecalho,
            "totalMovimentacoes": len(movimentacoes),
            "totalDocumentos": len(docs_raw),
            "movimentacoes": movimentacoes,
        }

    except Exception as e:
        logger.exception(f"Erro na consulta MNI: {e}")
        return {"sucesso": False, "erro": f"Erro na comunicação com o PROJUDI: {str(e)}"}


def mapear_dados_mni_para_processo(mni_data: Dict[str, Any]) -> Dict[str, Any]:
    """Converte dados MNI para o formato do schema ProcessoCreate."""
    cab = mni_data["cabecalho"]
    numero = cab.get("numero", "")

    # Formatar número CNJ
    if len(numero) == 20 and "-" not in numero:
        numero = f"{numero[:7]}-{numero[7:9]}.{numero[9:13]}.{numero[13]}.{numero[14:16]}.{numero[16:]}"

    # Parse data de distribuição
    data_ajuiz = None
    dist_str = cab.get("DataDistribuicao", "")
    if dist_str:
        try:
            data_ajuiz = datetime.strptime(dist_str[:10], "%d/%m/%Y")
        except Exception:
            pass

    status = cab.get("ProcessoStatus", "Ativo")
    # Normalizar status
    status_map = {"ARQUIVADO": "Arquivado", "ATIVO": "Ativo", "SUSPENSO": "Suspenso"}
    status = status_map.get(status.upper(), status)

    return {
        "numero_processo": numero,
        "tribunal": "TJGO",
        "grau": "G1",
        "data_ajuizamento": data_ajuiz,
        "nivel_sigilo": cab.get("nivelSigilo", 0),
        "classe_codigo": cab.get("classeProcessual"),
        "classe_nome": None,  # MNI usa código, nome virá do complemento
        "orgao_julgador_codigo": cab.get("codigoOrgao"),
        "orgao_julgador_nome": cab.get("orgaoJulgador", ""),
        "formato_nome": "Eletrônico",
        "sistema_nome": "PROJUDI",
        "titulo": f"Processo {numero}",
        "status": status,
        "prioridade": "Normal",
        "valor_causa": cab.get("valorCausa"),
        "area_direito": cab.get("Area"),
        "fase_processual": cab.get("ProcessoFase"),
    }


def extrair_partes_mni(mni_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai partes para o formato ProcessoParteCreate."""
    resultado = []
    for parte in mni_data["cabecalho"].get("partes", []):
        advogados = parte.get("advogados", [])
        # Se tem múltiplos advogados, serializa todos
        adv_nomes = ", ".join([a["nome"] for a in advogados]) if advogados else None
        adv_oabs = ", ".join([a["inscricao"] for a in advogados]) if advogados else None

        resultado.append({
            "tipo_parte": parte["polo"],
            "nome": parte["nome"],
            "cpf_cnpj": parte.get("documento"),
            "tipo_pessoa": parte.get("tipo_pessoa", "Física"),
            "advogado_nome": adv_nomes,
            "advogado_oab": adv_oabs,
        })
    return resultado


def extrair_movimentacoes_mni(mni_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai movimentações para o formato MovimentacaoCreate."""
    resultado = []
    for mov in mni_data.get("movimentacoes", []):
        nome = mov.get("descricao") or "Movimentação importada"
        complemento = mov.get("complemento", "")

        # Monta complementos_json com docs vinculados
        comp_data = {}
        if complemento:
            comp_data["texto"] = complemento
        if mov.get("documentos"):
            comp_data["documentos"] = mov["documentos"]

        resultado.append({
            "tipo": "externa",
            "codigo_movimento": mov.get("codigoNacional"),
            "nome_movimento": nome,
            "complementos_json": json.dumps(comp_data, ensure_ascii=False) if comp_data else None,
            "data_hora": mov.get("dataISO"),
        })
    return resultado


def extrair_assuntos_mni(mni_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrai assuntos — MNI do TJGO traz via classeProcessual."""
    cod = mni_data["cabecalho"].get("classeProcessual")
    if cod:
        return [{"codigo_tpu": cod, "nome": f"Classe {cod}", "principal": True}]
    return []


def analisar_processo_com_ia(
    mni_data: Dict[str, Any],
    movimentacoes_db: list,
    gemini_api_key: str
) -> Optional[Dict[str, Any]]:
    """
    Gera análise inteligente do processo usando o Gemini AI.
    Aceita dados MNI brutos OU movimentações já salvas no banco.
    """
    if not gemini_api_key:
        return {"erro": "Chave Gemini não configurada."}

    api_key = gemini_api_key.strip()

    # Montar contexto das movimentações
    movs_text_lines = []
    if mni_data and mni_data.get("movimentacoes"):
        # Usa dados MNI diretos (mais ricos)
        cab = mni_data.get("cabecalho", {})
        for mov in mni_data["movimentacoes"][:30]:
            entry = f"[{mov['data']}] {mov.get('descricao', '')}"
            if mov.get("complemento"):
                entry += f" - {mov['complemento']}"
            if mov.get("documentos"):
                docs = ", ".join([d.get("descricao", d.get("tipoArquivo", "")) for d in mov["documentos"] if d])
                if docs:
                    entry += f" (Docs: {docs})"
            movs_text_lines.append(entry)

        partes_text = "\n".join([
            f"  - {p['nome']} ({p['polo']})" for p in cab.get("partes", [])
        ])
        numero = cab.get("numero", "N/A")
        orgao = cab.get("orgaoJulgador", "N/A")
        status = cab.get("ProcessoStatus", "N/A")
        fase = cab.get("ProcessoFase", "N/A")
        area = cab.get("Area", "N/A")
        valor = cab.get("valorCausa", 0)
    else:
        # Fallback: usa movimentações do banco
        for mov in movimentacoes_db[:30]:
            dt = mov.data_hora.strftime("%d/%m/%Y %H:%M") if mov.data_hora else ""
            entry = f"[{dt}] {mov.nome_movimento}"
            if mov.complementos_json:
                try:
                    comp = json.loads(mov.complementos_json)
                    if isinstance(comp, dict) and comp.get("texto"):
                        entry += f" - {comp['texto']}"
                except Exception:
                    entry += f" - {mov.complementos_json[:200]}"
            movs_text_lines.append(entry)

        partes_text = "Não disponível"
        numero = "N/A"
        orgao = "N/A"
        status = "N/A"
        fase = "N/A"
        area = "N/A"
        valor = 0

    movs_text = "\n".join(movs_text_lines)

    prompt = f"""Voce e um assistente juridico especializado em Direito Processual Civil brasileiro.

Analise os dados abaixo de um processo judicial real e extraia:
1. Status atual do processo (em que fase esta, qual a ultima decisao relevante)
2. Acoes pendentes do advogado - O que precisa ser feito? Quais prazos estao correndo?
3. Prazos calculados com base no CPC e nas datas das intimacoes (dias uteis)
4. Alertas de urgencia - Prazos proximos de vencer ou ja vencidos
5. Resumo da historia processual - Narrativa breve

## DADOS DO PROCESSO

**Numero:** {numero}
**Orgao Julgador:** {orgao}
**Status:** {status}
**Fase:** {fase}
**Area:** {area}
**Valor da Causa:** R$ {valor:,.2f}

**Partes:**
{partes_text}

## MOVIMENTACOES (da mais recente para a mais antiga)

{movs_text}

## INSTRUCOES DE FORMATO

Responda em formato JSON com a seguinte estrutura:
```json
{{
  "statusAtual": "descricao do status atual do processo",
  "resumoHistoria": "narrativa breve da historia processual",
  "tarefasPendentes": [
    {{
      "acao": "O que deve ser feito",
      "responsavel": "Quem deve fazer",
      "prazoDataFim": "Data estimada de fim do prazo (DD/MM/YYYY) ou null",
      "prazoDiasUteis": numero_de_dias_uteis_ou_null,
      "urgencia": "CRITICA|ALTA|MEDIA|BAIXA|INFORMATIVA",
      "observacao": "qualquer observacao relevante"
    }}
  ],
  "alertas": [
    {{
      "tipo": "PRAZO_VENCENDO|PRAZO_VENCIDO|DECISAO_IMPORTANTE|INTIMACAO_PENDENTE",
      "mensagem": "descricao do alerta",
      "urgencia": "CRITICA|ALTA|MEDIA|BAIXA"
    }}
  ],
  "proximosPassos": [
    "Passo 1...",
    "Passo 2..."
  ]
}}
```

IMPORTANTE:
- Considere a data de HOJE como {datetime.now().strftime('%d/%m/%Y')}
- Prazos processuais contam em DIAS UTEIS (exceto sabados, domingos e feriados)
- Se o processo esta arquivado, considere se ha tarefas remanescentes
- Foque nas acoes que dependem do advogado
"""

    # Chamar Gemini REST API
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for modelo in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/{modelo}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                res_data = resp.json()
                candidates = res_data.get("candidates", [])
                if candidates:
                    texto = candidates[0]["content"]["parts"][0]["text"].strip()
                    # Extrair JSON
                    clean = texto.replace("```json", "").replace("```", "").strip()
                    json_start = clean.find("{")
                    json_end = clean.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        try:
                            return json.loads(clean[json_start:json_end])
                        except json.JSONDecodeError:
                            return {"textoRaw": texto}
                    return {"textoRaw": texto}

            if resp.status_code != 404:
                err = resp.json().get("error", {}).get("message", "")
                logger.warning(f"Gemini {modelo}: {resp.status_code} - {err[:150]}")

        except Exception as e:
            logger.warning(f"Gemini {modelo}: {e}")
            continue

    return {"erro": "Nenhum modelo Gemini respondeu. Verifique sua chave de API."}
