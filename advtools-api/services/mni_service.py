"""
Serviço de integração com o WebService MNI/PROJUDI TJGO.
Consulta processos, extrai movimentações enriquecidas, partes e documentos
via SOAP, e opcionalmente analisa com Gemini AI.
"""
import json
import logging
import requests
import re
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


def _limpar_numero_processo(numero: str) -> str:
    """Limpa o número apenas se parecer um CNJ (contém pontos ou traços)."""
    if any(c in numero for c in ".-"):
        return numero.replace(".", "").replace("-", "").strip()
    return numero.strip()


def _detectar_tribunal(numero: str) -> Optional[str]:
    """Detecta o tribunal pela posição J.TT do número CNJ."""
    limpo = _limpar_numero_processo(numero)
    if len(limpo) != 20:
        return None
    justica = limpo[13]
    tribunal_cod = limpo[14:16]
    cod_map = {("8", "09"): "TJGO"}
    return cod_map.get((justica, tribunal_cod))


def _tentar_completar_cnj_tjgo(numero: str) -> List[str]:
    """
    Tenta completar um número curto (N.DD ou N-DD) para um CNJ completo do TJGO.
    Retorna uma lista de candidatos ordenados por probabilidade.
    """
    limpo = numero.replace(".", "").replace("-", "").strip()
    if not limpo.isdigit() or len(limpo) < 5 or len(limpo) > 12:
        return []

    # Extrair NNNNNNN e DD (se houver pelo menos 3 dígitos)
    # Supondo que os últimos 2 são o DD
    n_seq = int(limpo[:-2])
    dd_alvo = int(limpo[-2:])
    
    candidatos = []
    # Testar anos recentes e forums comuns (0051=Goiania, etc)
    # TJGO tem aprox 180 comarcas
    for ano in range(datetime.now().year, 2010, -1):
        for forum in range(1, 185):
            # Calculo MOD 97 do CNJ
            # NNNNNNN DD AAAA J TR OOOO
            # Concatenado = NNNNNNNAAAAJTROOOO00
            n7 = f"{n_seq:07d}"
            a4 = f"{ano:04d}"
            jtr = "809"
            o4 = f"{forum:04d}"
            concat = int(f"{n7}{a4}{jtr}{o4}00")
            dd_calc = 98 - (concat % 97)
            
            if dd_calc == dd_alvo:
                candidatos.append(f"{n7}{dd_alvo:02d}{a4}809{o4}")
                
    # Ordenar: priorizar forums comuns (Goiânia=51, Aparecida=11, Anápolis=6)
    vips = {"0051", "0011", "0006"}
    def prioridade(c):
        forum = c[-4:]
        return 0 if forum in vips else 1

    return sorted(candidatos, key=prioridade)


def suporta_mni(numero: str) -> bool:
    """Verifica se o número pertence a um tribunal com MNI configurado ou se é um ID interno compatível."""
    if not numero: return False
    
    # Se for CNJ (20 dígitos), detecta tribunal
    limpo = _limpar_numero_processo(numero)
    if len(limpo) == 20:
        tribunal = _detectar_tribunal(limpo)
        return tribunal in TRIBUNAIS_MNI
    
    # Se não for CNJ, mas o usuário estiver tentando usar via MNI (frontend decidirá),
    # aqui retornamos True se o identificador parecer um ID interno do Projudi (numérico longo)
    return numero.isdigit() and len(numero) > 5


def consultar_processo_mni(numero_processo: str) -> Dict[str, Any]:
    """Consulta processo completo via MNI/SOAP e retorna dados estruturados."""
    from zeep import Client
    from zeep.settings import Settings

    numero_limpo = _limpar_numero_processo(numero_processo)

    if not Config.PROJUDI_USER or not Config.PROJUDI_PASSWORD:
        return {"sucesso": False, "erro": "Credenciais do PROJUDI não configuradas (PROJUDI_USER/PASSWORD)."}

    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        client = Client(wsdl=WSDL_URL, settings=settings)

        # Tentar completar se não for um CNJ válido
        candidatos = [numero_limpo]
        if len(numero_limpo) != 20:
            candidatos = _tentar_completar_cnj_tjgo(numero_processo)
            if not candidatos:
                return {"sucesso": False, "erro": "Formato de número inválido para busca MNI/TJGO."}

        # Tentar cada candidato até um ter sucesso técnico (mesmo que processo não exista)
        # O WebService retorna sucesso=False se o processo não existe, mas sucesso=True se a busca foi válida.
        ultimo_erro = "Processo não encontrado nos candidatos tentados."
        
        for cand in candidatos[:10]: # Limitar tentativas para performance
            try:
                response = client.service.consultarProcesso(
                    idConsultante=Config.PROJUDI_USER,
                    senhaConsultante=Config.PROJUDI_PASSWORD,
                    numeroProcesso=cand,
                    movimentos=True,
                    incluirCabecalho=True,
                    incluirDocumentos=True
                )
                
                if response.sucesso:
                    # Encontramos o processo!
                    break
                else:
                    ultimo_erro = response.mensagem or "Processo não encontrado."
                    # Se o erro for de formato (como o do usuário), ignora e tenta o próximo
                    continue
            except Exception as e:
                ultimo_erro = str(e)
                continue
        else:
            return {"sucesso": False, "erro": ultimo_erro}

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


def listar_processos_advogado_mni() -> Dict[str, Any]:
    """
    Consulta avisos pendentes do PROJUDI via MNI e retorna lista de números de processo únicos.
    Retorna: {"sucesso": bool, "numeros": [...], "total_avisos": int, "erro": str}
    """
    from zeep import Client
    from zeep.settings import Settings

    if not Config.PROJUDI_USER or not Config.PROJUDI_PASSWORD:
        return {"sucesso": False, "numeros": [], "total_avisos": 0, "erro": "Credenciais do PROJUDI não configuradas."}

    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        client = Client(wsdl=WSDL_URL, settings=settings)

        response = client.service.consultarAvisosPendentes(
            idConsultante=Config.PROJUDI_USER,
            senhaConsultante=Config.PROJUDI_PASSWORD,
            idRepresentado=Config.PROJUDI_USER
        )

        if not response.sucesso:
            return {"sucesso": False, "numeros": [], "total_avisos": 0, "erro": response.mensagem or "Falha ao consultar avisos."}

        avisos = getattr(response, 'aviso', []) or []
        numeros_unicos = set()

        for aviso in avisos:
            proc_aviso = getattr(aviso, 'processo', None)
            if proc_aviso:
                numero = getattr(proc_aviso, 'numero', None)
                if numero:
                    numeros_unicos.add(str(numero))

        return {
            "sucesso": True,
            "numeros": list(numeros_unicos),
            "total_avisos": len(avisos),
            "erro": None
        }

    except Exception as e:
        logger.exception(f"Erro ao listar processos via MNI: {e}")
        return {"sucesso": False, "numeros": [], "total_avisos": 0, "erro": f"Erro na comunicação com o PROJUDI: {str(e)}"}


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
        # Ordenar por data decrescente (mais recentes primeiro)
        movs = sorted(mni_data["movimentacoes"], key=lambda m: m.get("dataISO") or "", reverse=True)
        # Regime equilibrado: as 30 últimas para fornecer contexto adequado sem estourar cota
        for mov in movs[:30]:
            entry = f"[{mov['data']}] {mov.get('descricao', '')}"
            if mov.get("complemento"):
                entry += f" - {mov['complemento']}"
            movs_text_lines.append(entry)

        numero = cab.get("numero", "N/A")
    else:
        # Fallback: usa movimentações do banco
        # Ordenar por data decrescente
        movs = sorted(movimentacoes_db, key=lambda m: m.data_hora.replace(tzinfo=None) if m.data_hora else datetime.min, reverse=True)
        # Regime equilibrado: as 30 últimas
        for mov in movs[:30]:
            dt = mov.data_hora.strftime("%d/%m/%Y %H:%M") if mov.data_hora else ""
            entry = f"[{dt}] {mov.nome_movimento}"
            if mov.complementos_json:
                try:
                    comp = json.loads(mov.complementos_json)
                    if isinstance(comp, dict) and comp.get("texto"):
                        entry += f" - {comp['texto']}"
                except Exception:
                    pass
            movs_text_lines.append(entry)
        numero = "N/A"

    movs_text = "\n".join(movs_text_lines)
    hoje = datetime.now().strftime("%d/%m/%Y")
 
    prompt = f"""Analise as 30 MOVIMENTACOES RECENTES do processo {numero} e retorne em JSON.
    
DATA DE HOJE: {hoje}
 
MOVIMENTACOES:
{movs_text}
 
INSTRUÇÕES DE PRAZO:
1. Se a movimentação cita um prazo (ex: 'prazo de 15 dias'), CALCULE a data de vencimento somando os dias à data daquela movimentação específica.
2. Se NÃO houver prazo explícito na movimentação, mas a ação for necessária (ex: 'Pagar custas'), INfIRA um prazo razoável baseado na lei (ex: +15 dias corridos a partir de hoje).
3. O campo 'prazoDataFim' deve sempre conter uma data no formato DD/MM/YYYY. NUNCA use 'null', 'a definir' ou texto. ESTIME uma data se necessário.
 
JSON esperado (MANTENHA EXATAMENTE ESTA ESTRUTURA):
{{
  "statusAtual": "Momento resumido do processo",
  "resumoHistoria": "breve contexto do que aconteceu até agora",
  "tarefasPendentes": [
    {{
      "acao": "Título curto e direto da tarefa",
      "prazoDataFim": "DD/MM/YYYY", 
      "urgencia": "ALTA, MEDIA ou BAIXA"
    }}
  ],
  "alertas": [{{"tipo": "PRAZO", "mensagem": "..."}}],
  "proximosPassos": ["..."]
}}
"""



    # Chamar Gemini REST API
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}

    # Lista baseada nos modelos estáveis e aliases disponíveis (list_all_models.py)
    MODELOS_TENTAR = [
        "models/gemini-1.5-flash",
        "models/gemini-flash-latest",
        "models/gemini-1.5-pro",
        "models/gemini-pro-latest",
    ]
    API_VERSIONS = ["v1", "v1beta"]

    ultimo_erro = "Nenhum modelo respondeu"
    
    for modelo in MODELOS_TENTAR:
        for version in API_VERSIONS:
            url = f"https://generativelanguage.googleapis.com/{version}/{modelo}:generateContent?key={api_key}"
            print(f" >>> [IA - Tentativa] {version} | {modelo}")
            try:
                # Timeout otimizado
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                print(f" >>> [IA - Resposta] Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    res_data = resp.json()
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        texto = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                        if texto:
                            print(f" >>> [IA - Sucesso] Modelo {modelo} respondeu.")
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
                
                # Se não for 200, logamos o erro para saber o que houve
                try:
                    raw_err = resp.text[:200]
                    print(f" >>> [IA - Detalhe] Body: {raw_err}")
                except:
                    pass
                
                # ERRO DE COTA (429) - O mais importante para o usuário final
                if resp.status_code == 429:
                    try:
                        err_json = resp.json()
                        msg_google = err_json.get("error", {}).get("message", "Sem detalhe")
                        reason = err_json.get("error", {}).get("status", "")
                    except:
                        msg_google = resp.text[:200]
                        reason = "UNKNOWN"
                    
                    print(f" >>> [IA - 429] Status: {reason} | Msg: {msg_google}")
                    
                    # Tenta extrair o tempo de espera (ex: retry in 49.9s)
                    match = re.search(r'retry in (\d+\.?\d*)s', msg_google)
                    if match:
                        segundos = int(float(match.group(1)))
                        return {
                            "erro": f"⏳ Frequência Excedida: O Google pediu para aguardar {segundos} segundos. Motivo: {msg_google}"
                        }
                    
                    # Mensagem amigável mas técnica
                    return {
                        "erro": f"⚖️ Cota Gemini: {msg_google}. Se você não usou a IA hoje, verifique na console do Google se sua chave não está restrita ou se o Billing está OK (mesmo no plano Free)."
                    }

                # Se for erro de autenticação (403)
                if resp.status_code == 403:
                    return {"erro": "Acesso Negado (403): Verifique se sua chave de API do Gemini no Escritório está correta e ativa."}

                # Outros erros (404, etc)
                if resp.status_code != 404:
                    try:
                        err_msg = resp.json().get("error", {}).get("message", "")
                    except:
                        err_msg = resp.text[:100]
                    ultimo_erro = f"({resp.status_code}) {err_msg}"

            except requests.exceptions.Timeout:
                ultimo_erro = "Timeout (O servidor do Google demorou a responder)"
                continue
            except Exception as e:
                ultimo_erro = f"Erro de conexão: {str(e)}"
                continue



    return {"erro": f"Nenhum modelo Gemini respondeu. Detalhe: {ultimo_erro}. Verifique sua chave de API nas configurações do escritório ou no arquivo .env."}



