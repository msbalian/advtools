import time
import requests
import os
import json
from dotenv import load_dotenv

# Importando as funções do nosso banco de dados
from database import buscar_todos_processos, salvar_ou_atualizar_processo

# Carrega a API Key do arquivo .env
load_dotenv()
API_KEY = os.getenv("DATAJUD_KEY")

def consultar_api_datajud(numero_processo, tribunal):
    """Consulta a API e retorna o dicionário limpo"""
    url = f"https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal.lower()}/_search"
    
    headers = {
        "Authorization": f"APIKey {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": {
            "match": {
                "numeroProcesso": numero_processo
            }
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            if dados['hits']['total']['value'] > 0:
                source = dados['hits']['hits'][0]['_source']
                
                # --- CORREÇÃO AQUI ---
                # Alguns tribunais usam 'movimentos', outros 'movimentacoes'.
                # Vamos tentar pegar 'movimentos' primeiro, se não tiver, tenta 'movimentacoes'.
                movs = source.get('movimentos') or source.get('movimentacoes') or []
                
                # Pega a movimentação mais recente (a primeira da lista)
                if movs:
                    ultima_mov = movs[0].get('nome')
                    data_mov = movs[0].get('dataHora')
                else:
                    ultima_mov = "Sem movimentações registradas"
                    data_mov = None

                return {
                    "sucesso": True,
                    "numero": source.get('numeroProcesso'),
                    "tribunal": tribunal,
                    "classe": source.get('classe', {}).get('nome'),
                    "ultima_movimentacao": ultima_mov,
                    "data_atualizacao": source.get('dataHoraUltimaAtualizacao')
                }
            else:
                return {"sucesso": False, "erro": "Processo não encontrado no DataJud"}
        else:
            return {"sucesso": False, "erro": f"Erro API: {response.status_code}"}
            
    except Exception as e:
        return {"sucesso": False, "erro": f"Erro de Conexão: {str(e)}"}

def rodar_sincronizacao():
    print("🔄 Iniciando Sincronização do ADVtools (Versão Corrigida)...")
    
    # 1. Busca todos os processos cadastrados no banco
    processos = buscar_todos_processos()
    print(f"📂 Processos na fila: {len(processos)}")
    
    # 2. Loop de atualização
    for proc in processos:
        numero_proc = proc[0] 
        tribunal_proc = proc[1]
        
        print(f"   👉 Verificando: {numero_proc} ({tribunal_proc})...", end="")
        
        resultado = consultar_api_datajud(numero_proc, tribunal_proc)
        
        if resultado['sucesso']:
            # Mantemos o nome do cliente original
            resultado['cliente'] = proc[2] 
            salvar_ou_atualizar_processo(resultado)
            print(f" ✅ Atualizado! Movimento: {resultado['ultima_movimentacao'][:30]}...") 
        else:
            print(f" ❌ Falha: {resultado['erro']}")
        
        time.sleep(2)

    print("🏁 Sincronização Finalizada!")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ ERRO: Verifique seu arquivo .env")
    else:
        rodar_sincronizacao()