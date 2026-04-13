"""
PoC: Extração inteligente de PRAZOS e AÇÕES do advogado
usando dados MNI + Gemini AI

Pipeline:  MNI (movimentações) → Gemini → Tarefas estruturadas
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

PROJUDI_USER = os.getenv("PROJUDI_USER", "")
PROJUDI_PASSWORD = os.getenv("PROJUDI_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
WSDL_URL = "https://projudi.tjgo.jus.br/IntercomunicacaoService?WSDL"
PROCESSO_TESTE = "57602432220258090051"

OUTPUT_DIR = Path(__file__).parent / "poc_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def buscar_processo_mni():
    """Busca processo completo via MNI e extrai dados estruturados."""
    from zeep import Client
    from zeep.settings import Settings

    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, settings=settings)

    print("[MNI] Consultando processo...")
    response = client.service.consultarProcesso(
        idConsultante=PROJUDI_USER,
        senhaConsultante=PROJUDI_PASSWORD,
        numeroProcesso=PROCESSO_TESTE,
        movimentos=True,
        incluirCabecalho=True,
        incluirDocumentos=True
    )

    if not response.sucesso:
        print(f"[ERRO] {response.mensagem}")
        return None

    proc = response.processo
    dados = proc.dadosBasicos

    # Extrair cabecalho
    cabecalho = {
        "numero": getattr(dados, 'numero', ''),
        "classeProcessual": getattr(dados, 'classeProcessual', ''),
        "valorCausa": getattr(dados, 'valorCausa', 0),
        "nivelSigilo": getattr(dados, 'nivelSigilo', 0),
    }

    # Orgao julgador
    orgao = getattr(dados, 'orgaoJulgador', None)
    if orgao:
        cabecalho["orgaoJulgador"] = getattr(orgao, 'nomeOrgao', '')

    # Partes (resumo)
    polos = getattr(dados, 'polo', [])
    partes = []
    advogados_cliente = []
    for polo in polos:
        tipo_polo = getattr(polo, 'polo', '')
        for parte in getattr(polo, 'parte', []):
            pessoa = getattr(parte, 'pessoa', None)
            if pessoa:
                nome = getattr(pessoa, 'nome', '')
                partes.append({"nome": nome, "polo": tipo_polo})
            for adv in (getattr(parte, 'advogado', []) or []):
                adv_nome = getattr(adv, 'nome', '')
                adv_oab = getattr(adv, 'inscricao', '')
                if "NUBIA" in adv_nome.upper() or "BALIAN" in adv_nome.upper():
                    advogados_cliente.append({
                        "nome": adv_nome,
                        "oab": adv_oab,
                        "parte": nome,
                        "polo": tipo_polo
                    })

    cabecalho["partes"] = partes
    cabecalho["advogadosDoEscritorio"] = advogados_cliente

    # Extrair parametros extras
    outros = getattr(dados, 'outroParametro', []) or []
    for p in outros:
        nome_p = getattr(p, 'nome', '')
        valor_p = getattr(p, 'valor', '')
        if nome_p in ('ProcessoStatus', 'ProcessoFase', 'Area', 'DataDistribuicao'):
            cabecalho[nome_p] = valor_p

    # Movimentacoes (enriquecidas com documentos vinculados)
    movs_raw = getattr(proc, 'movimento', []) or []
    docs_raw = getattr(proc, 'documento', []) or []

    # Criar mapa de documentos
    doc_map = {}
    for doc in docs_raw:
        doc_id = getattr(doc, 'idDocumento', '')
        outros_doc = getattr(doc, 'outroParametro', []) or []
        nome_arq = ''
        tipo_arq = ''
        for p in outros_doc:
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

    movimentacoes = []
    for mov in movs_raw:
        dt_str = getattr(mov, 'dataHora', '')
        id_mov = getattr(mov, 'identificadorMovimento', '')

        # Movimento nacional
        mov_nac = getattr(mov, 'movimentoNacional', None)
        cod_nac = getattr(mov_nac, 'codigoNacional', 0) if mov_nac else 0

        # Movimento local
        mov_loc = getattr(mov, 'movimentoLocal', None)
        desc_loc = getattr(mov_loc, 'descricao', '') if mov_loc else ''

        # Complementos
        comps = getattr(mov, 'complemento', []) or []
        complemento = ' '.join([str(c) for c in comps if c]) if comps else ''

        # Documentos vinculados
        docs_vinc_ids = getattr(mov, 'idDocumentoVinculado', []) or []
        docs_vinc = [doc_map.get(str(d), {"id": str(d)}) for d in docs_vinc_ids]

        # Parse data
        dt_formatted = ''
        if dt_str and len(str(dt_str)) >= 8:
            try:
                dt_obj = datetime.strptime(str(dt_str)[:14], '%Y%m%d%H%M%S')
                dt_formatted = dt_obj.strftime('%d/%m/%Y %H:%M')
            except Exception:
                dt_formatted = str(dt_str)

        movimentacoes.append({
            "data": dt_formatted,
            "dataRaw": str(dt_str),
            "idMovimento": str(id_mov),
            "codigoNacional": cod_nac,
            "descricao": desc_loc,
            "complemento": complemento,
            "documentos": docs_vinc if docs_vinc else None
        })

    resultado = {
        "cabecalho": cabecalho,
        "totalMovimentacoes": len(movimentacoes),
        "movimentacoes": movimentacoes
    }

    print(f"[MNI] Processo carregado: {cabecalho['numero']}")
    print(f"[MNI] {len(movimentacoes)} movimentacoes, {len(docs_raw)} documentos")

    return resultado


def analisar_com_gemini(processo_data):
    """Envia dados do processo para o Gemini via REST API (mesmo padrao do ai_service.py)."""
    import requests as http_requests

    MODELOS = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash",
    ]
    API_VERSIONS = ["v1beta"]

    # Preparar contexto para o Gemini - Ultimas 30 movs mais relevantes
    movs_relevantes = []
    for mov in processo_data["movimentacoes"][:30]:
        entry = f"[{mov['data']}] {mov['descricao']}"
        if mov['complemento']:
            entry += f" - {mov['complemento']}"
        if mov.get('documentos'):
            docs_desc = ', '.join([d.get('descricao', d.get('tipoArquivo', '')) for d in mov['documentos'] if d])
            entry += f" (Docs: {docs_desc})"
        movs_relevantes.append(entry)

    movs_text = '\n'.join(movs_relevantes)

    cabecalho = processo_data["cabecalho"]
    partes_text = '\n'.join([f"  - {p['nome']} (Polo {'Ativo' if p['polo']=='AT' else 'Passivo'})" for p in cabecalho.get('partes', [])])
    advs_text = '\n'.join([f"  - {a['nome']} (OAB {a['oab']}) - representa {a['parte']}" for a in cabecalho.get('advogadosDoEscritorio', [])])

    prompt = f"""Voce e um assistente juridico especializado em Direito Processual Civil brasileiro.

Analise os dados abaixo de um processo judicial real e extraia:
1. **Status atual do processo** (em que fase esta, qual a ultima decisao relevante)
2. **Acoes pendentes do advogado** - O que a advogada Nubia precisa fazer? Quais prazos estao correndo?
3. **Prazos calculados** - Com base no CPC e nas datas das intimacoes, calcule os prazos em dias uteis
4. **Alertas de urgencia** - Prazos que estao proximos de vencer ou ja venceram
5. **Resumo da historia processual** - Narrativa breve do que aconteceu neste processo

## DADOS DO PROCESSO

**Numero:** {cabecalho.get('numero', 'N/A')}
**Orgao Julgador:** {cabecalho.get('orgaoJulgador', 'N/A')}
**Status:** {cabecalho.get('ProcessoStatus', 'N/A')}
**Fase:** {cabecalho.get('ProcessoFase', 'N/A')}
**Area:** {cabecalho.get('Area', 'N/A')}
**Valor da Causa:** R$ {cabecalho.get('valorCausa', 0):,.2f}

**Partes:**
{partes_text}

**Advogados do nosso escritorio:**
{advs_text}

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
      "responsavel": "Quem deve fazer (advogado, parte, tribunal)",
      "prazoOrigem": "Movimentacao que originou o prazo",
      "prazoDataInicio": "Data de inicio do prazo (DD/MM/YYYY)",
      "prazoDataFim": "Data estimada de fim do prazo (DD/MM/YYYY) ou null",
      "prazoDiasUteis": numero_de_dias_uteis_ou_null,
      "urgencia": "CRITICA|ALTA|MEDIA|BAIXA|INFORMATIVA",
      "status": "PENDENTE|CUMPRIDA|EXPIRADA",
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
- Foque nas acoes que dependem da advogada Nubia
"""

    print("[GEMINI] Enviando analise para o Gemini (REST API)...")
    print(f"[GEMINI] Prompt: {len(prompt)} caracteres")

    api_key = GEMINI_API_KEY.strip()
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}

    ultimo_erro = "Nenhum modelo respondeu"
    for modelo in MODELOS:
        for version in API_VERSIONS:
            url = f"https://generativelanguage.googleapis.com/{version}/{modelo}:generateContent?key={api_key}"
            try:
                resp = http_requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200:
                    res_data = resp.json()
                    if 'candidates' in res_data and len(res_data['candidates']) > 0:
                        texto_resposta = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                        print(f"[GEMINI] Resposta recebida ({modelo}): {len(texto_resposta)} chars")

                        # Extrair JSON
                        clean = texto_resposta.replace('```json', '').replace('```', '').strip()
                        json_start = clean.find('{')
                        json_end = clean.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            try:
                                return json.loads(clean[json_start:json_end])
                            except json.JSONDecodeError:
                                print("[AVISO] JSON invalido, retornando texto bruto")
                                return {"textoRaw": texto_resposta}
                        return {"textoRaw": texto_resposta}

                if resp.status_code != 404:
                    err_msg = resp.json().get("error", {}).get("message", "Erro desconhecido")
                    ultimo_erro = f"({resp.status_code}) {err_msg}"
                    print(f"[GEMINI] {modelo}/{version}: {ultimo_erro}")

            except Exception as e:
                ultimo_erro = str(e)
                continue

    print(f"[ERRO GEMINI] {ultimo_erro}")
    return None


def exibir_resultado(analise):
    """Formata e exibe o resultado da analise."""
    if not analise:
        print("\n[ERRO] Sem resultado para exibir")
        return

    if "textoRaw" in analise:
        print("\n" + "=" * 70)
        print("  ANALISE DO GEMINI (texto bruto)")
        print("=" * 70)
        print(analise["textoRaw"])
        return

    print("\n" + "=" * 70)
    print("  ANALISE INTELIGENTE DO PROCESSO")
    print("=" * 70)

    # Status
    print(f"\n  STATUS ATUAL:")
    print(f"  {analise.get('statusAtual', 'N/A')}")

    # Resumo
    print(f"\n  HISTORIA PROCESSUAL:")
    print(f"  {analise.get('resumoHistoria', 'N/A')}")

    # Alertas
    alertas = analise.get('alertas', [])
    if alertas:
        print(f"\n  ALERTAS ({len(alertas)}):")
        print("  " + "-" * 50)
        for alerta in alertas:
            icon = {"CRITICA": "!!!!", "ALTA": "!!!", "MEDIA": "!!", "BAIXA": "!", "INFORMATIVA": "i"}.get(alerta.get('urgencia', ''), '?')
            tipo = alerta.get('tipo', '')
            msg = alerta.get('mensagem', '')
            print(f"  [{icon}] [{tipo}] {msg}")

    # Tarefas
    tarefas = analise.get('tarefasPendentes', [])
    if tarefas:
        print(f"\n  TAREFAS PENDENTES ({len(tarefas)}):")
        print("  " + "-" * 50)
        for i, tarefa in enumerate(tarefas, 1):
            urg = tarefa.get('urgencia', 'N/A')
            status = tarefa.get('status', 'N/A')
            acao = tarefa.get('acao', 'N/A')
            resp = tarefa.get('responsavel', 'N/A')
            prazo_fim = tarefa.get('prazoDataFim', '')
            prazo_dias = tarefa.get('prazoDiasUteis', '')
            obs = tarefa.get('observacao', '')

            icon = {"CRITICA": "!!", "ALTA": "!", "MEDIA": "-", "BAIXA": ".", "INFORMATIVA": " "}.get(urg, "?")
            status_icon = {"PENDENTE": "[ ]", "CUMPRIDA": "[x]", "EXPIRADA": "[!]"}.get(status, "[?]")

            print(f"\n  {status_icon} Tarefa {i} [{urg}]")
            print(f"      Acao: {acao}")
            print(f"      Responsavel: {resp}")
            if prazo_fim:
                print(f"      Prazo: {prazo_fim} ({prazo_dias} dias uteis)" if prazo_dias else f"      Prazo: {prazo_fim}")
            if obs:
                print(f"      Obs: {obs}")

    # Proximos passos
    proximos = analise.get('proximosPassos', [])
    if proximos:
        print(f"\n  PROXIMOS PASSOS:")
        print("  " + "-" * 50)
        for i, passo in enumerate(proximos, 1):
            print(f"  {i}. {passo}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  PoC: EXTRACAO INTELIGENTE DE PRAZOS E ACOES")
    print(f"  Pipeline: MNI -> Gemini AI -> Tarefas Estruturadas")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)

    if not GEMINI_API_KEY:
        print("[ERRO] GEMINI_API_KEY nao configurada no .env")
        sys.exit(1)

    # Fase 1: Buscar dados via MNI
    processo_data = buscar_processo_mni()
    if not processo_data:
        print("[ERRO] Falha ao buscar processo")
        sys.exit(1)

    # Salvar dados brutos para referencia
    with open(OUTPUT_DIR / "processo_mni_dados.json", "w", encoding="utf-8") as f:
        json.dump(processo_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"[INFO] Dados MNI salvos em: {OUTPUT_DIR / 'processo_mni_dados.json'}")

    # Fase 2: Analisar com Gemini
    analise = analisar_com_gemini(processo_data)

    # Salvar analise
    if analise:
        with open(OUTPUT_DIR / "analise_gemini.json", "w", encoding="utf-8") as f:
            json.dump(analise, f, ensure_ascii=False, indent=2, default=str)
        print(f"[INFO] Analise salva em: {OUTPUT_DIR / 'analise_gemini.json'}")

    # Fase 3: Exibir resultado
    exibir_resultado(analise)

    print("\n" + "=" * 70)
    print("  FIM DA ANALISE")
    print("=" * 70)
