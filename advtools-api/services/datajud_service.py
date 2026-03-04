import requests
import json
from datetime import datetime
from config import Config
from typing import Optional, Dict, Any

# Mapeamentos do DataJud
TRIBUNAIS_DATAJUD = {
    # Justiça Estadual
    'TJAC': 'tjac', 'TJAL': 'tjal', 'TJAM': 'tjam', 'TJAP': 'tjap',
    'TJBA': 'tjba', 'TJCE': 'tjce', 'TJDFT': 'tjdft', 'TJES': 'tjes',
    'TJGO': 'tjgo', 'TJMA': 'tjma', 'TJMG': 'tjmg', 'TJMS': 'tjms',
    'TJMT': 'tjmt', 'TJPA': 'tjpa', 'TJPB': 'tjpb', 'TJPE': 'tjpe',
    'TJPI': 'tjpi', 'TJPR': 'tjpr', 'TJRJ': 'tjrj', 'TJRN': 'tjrn',
    'TJRO': 'tjro', 'TJRR': 'tjrr', 'TJRS': 'tjrs', 'TJSC': 'tjsc',
    'TJSE': 'tjse', 'TJSP': 'tjsp', 'TJTO': 'tjto',
    # TRFs
    'TRF1': 'trf1', 'TRF2': 'trf2', 'TRF3': 'trf3',
    'TRF4': 'trf4', 'TRF5': 'trf5', 'TRF6': 'trf6',
    # TRTs
    'TRT1': 'trt1', 'TRT2': 'trt2', 'TRT3': 'trt3', 'TRT4': 'trt4',
    'TRT5': 'trt5', 'TRT6': 'trt6', 'TRT7': 'trt7', 'TRT8': 'trt8',
    'TRT9': 'trt9', 'TRT10': 'trt10', 'TRT11': 'trt11', 'TRT12': 'trt12',
    'TRT13': 'trt13', 'TRT14': 'trt14', 'TRT15': 'trt15', 'TRT16': 'trt16',
    'TRT17': 'trt17', 'TRT18': 'trt18', 'TRT19': 'trt19', 'TRT20': 'trt20',
    'TRT21': 'trt21', 'TRT22': 'trt22', 'TRT23': 'trt23', 'TRT24': 'trt24',
    # Superiores
    'STF': 'stf', 'STJ': 'stj', 'TST': 'tst', 'TSE': 'tse', 'STM': 'stm',
}

_TRIBUNAL_POR_CODIGO = {
    # Justiça Estadual (J=8)
    ('8', '01'): 'TJAC', ('8', '02'): 'TJAL', ('8', '03'): 'TJAP',
    ('8', '04'): 'TJAM', ('8', '05'): 'TJBA', ('8', '06'): 'TJCE',
    ('8', '07'): 'TJDFT', ('8', '08'): 'TJES', ('8', '09'): 'TJGO',
    ('8', '10'): 'TJMA', ('8', '11'): 'TJMT', ('8', '12'): 'TJMS',
    ('8', '13'): 'TJMG', ('8', '14'): 'TJPA', ('8', '15'): 'TJPB',
    ('8', '16'): 'TJPR', ('8', '17'): 'TJPE', ('8', '18'): 'TJPI',
    ('8', '19'): 'TJRJ', ('8', '20'): 'TJRN', ('8', '21'): 'TJRS',
    ('8', '22'): 'TJRO', ('8', '23'): 'TJRR', ('8', '24'): 'TJSC',
    ('8', '25'): 'TJSE', ('8', '26'): 'TJSP', ('8', '27'): 'TJTO',
    # Justiça Federal (J=4)
    ('4', '01'): 'TRF1', ('4', '02'): 'TRF2', ('4', '03'): 'TRF3',
    ('4', '04'): 'TRF4', ('4', '05'): 'TRF5', ('4', '06'): 'TRF6',
    # Justiça do Trabalho (J=5)
    ('5', '01'): 'TRT1', ('5', '02'): 'TRT2', ('5', '03'): 'TRT3',
    ('5', '04'): 'TRT4', ('5', '05'): 'TRT5', ('5', '06'): 'TRT6',
    ('5', '07'): 'TRT7', ('5', '08'): 'TRT8', ('5', '09'): 'TRT9',
    ('5', '10'): 'TRT10', ('5', '11'): 'TRT11', ('5', '12'): 'TRT12',
    ('5', '13'): 'TRT13', ('5', '14'): 'TRT14', ('5', '15'): 'TRT15',
    ('5', '16'): 'TRT16', ('5', '17'): 'TRT17', ('5', '18'): 'TRT18',
    ('5', '19'): 'TRT19', ('5', '20'): 'TRT20', ('5', '21'): 'TRT21',
    ('5', '22'): 'TRT22', ('5', '23'): 'TRT23', ('5', '24'): 'TRT24',
}

def extrair_tribunal_do_numero(numero_cnj: str) -> Optional[str]:
    """Detecta o tribunal pelo número CNJ (ramo J e tribunal TT)."""
    try:
        limpo = numero_cnj.replace('.', '').replace('-', '')
        if len(limpo) != 20:
            return None
        justica = limpo[13]
        tribunal_cod = limpo[14:16]
        return _TRIBUNAL_POR_CODIGO.get((justica, tribunal_cod))
    except Exception:
        return None

def consultar_processo_datajud(numero_cnj: str, tribunal: Optional[str] = None) -> Dict[str, Any]:
    """Consulta os dados brutos de um processo no DataJud."""
    if not tribunal:
        tribunal = extrair_tribunal_do_numero(numero_cnj)
    
    if not tribunal or tribunal not in TRIBUNAIS_DATAJUD:
        return {"sucesso": False, "erro": f"Tribunal '{tribunal or '?'}' não reconhecido."}

    alias = TRIBUNAIS_DATAJUD[tribunal]
    url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{alias}/_search"
    
    headers = {
        'Authorization': f'APIKey {Config.DATAJUD_KEY}',
        'Content-Type': 'application/json',
    }
    
    body = {
        "query": {
            "match": {
                "numeroProcesso": numero_cnj.replace('.', '').replace('-', '')
            }
        },
        "size": 1
    }
    
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {"sucesso": False, "erro": f"Erro na consulta DataJud: {str(e)}"}
    
    hits = data.get('hits', {}).get('hits', [])
    if not hits:
        return {"sucesso": False, "erro": "Processo não encontrado na base DataJud."}
    
    return {"sucesso": True, "data": hits[0].get('_source', {}), "tribunal": tribunal}

def mapear_dados_datajud_para_processo(proc_data: Dict[str, Any], tribunal: str) -> Dict[str, Any]:
    """Mapeia os dados do DataJud para o formato do nosso modelo Processo."""
    classe = proc_data.get('classe', {})
    orgao = proc_data.get('orgaoJulgador', {})
    formato = proc_data.get('formato', {})
    sistema = proc_data.get('sistema', {})
    
    # Formatação de Datas
    def parse_dt(dt_str):
        if not dt_str: return None
        try:
            # Tenta formatos comuns de ISO
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return None

    return {
        "numero_processo": proc_data.get('numeroProcesso'),
        "tribunal": tribunal,
        "grau": proc_data.get('grau', 'G1'),
        "data_ajuizamento": parse_dt(proc_data.get('dataAjuizamento')),
        "nivel_sigilo": proc_data.get('nivelSigilo', 0),
        "classe_codigo": classe.get('codigo'),
        "classe_nome": classe.get('nome'),
        "orgao_julgador_codigo": orgao.get('codigo'),
        "orgao_julgador_nome": orgao.get('nome'),
        "orgao_julgador_municipio_ibge": orgao.get('codigoMunicipioIBGE'),
        "formato_codigo": formato.get('codigo'),
        "formato_nome": formato.get('nome', 'Eletrônico'),
        "sistema_codigo": sistema.get('codigo'),
        "sistema_nome": sistema.get('nome'),
        "titulo": classe.get('nome', f"Processo {proc_data.get('numeroProcesso')}"),
        "status": "Ativo",
        "prioridade": "Normal"
    }

def extrair_movimentacoes(proc_data: Dict[str, Any]) -> list:
    """Extrai as movimentações do JSON do DataJud."""
    movimentacoes = []
    for mov in proc_data.get('movimentos', []):
        complementos = mov.get('complementosTabelados', [])
        movimentacoes.append({
            "tipo": "externa",
            "codigo_movimento": mov.get('codigo'),
            "nome_movimento": mov.get('nome', 'Movimentação importada'),
            "complementos_json": json.dumps(complementos) if complementos else None,
            "data_hora": mov.get('dataHora') # String ISO que será convertida no CRUD/Model
        })
    return movimentacoes

def extrair_assuntos(proc_data: Dict[str, Any]) -> list:
    """Extrai os assuntos TPU do JSON do DataJud."""
    assuntos = []
    for ass in proc_data.get('assuntos', []):
        assuntos.append({
            "codigo_tpu": ass.get('codigo'),
            "nome": ass.get('nome', 'Assunto importado'),
            "principal": ass.get('principal', False)
        })
    return assuntos
