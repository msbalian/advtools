import os
import json
import requests
from typing import Dict, Any

# Lista de modelos para redundância (Nomes completos conforme exigido pela API)
MODELOS_DISPONIVEIS = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.5-pro",
    "models/gemini-pro"
]

# Versões da API para testar
API_VERSIONS = ["v1beta", "v1"]

async def redigir_documento_com_ia(api_key: str, modelo_texto: str, context: Dict[str, Any], instrucoes: str) -> str:
    """
    Usa o Gemini (via REST API) para redigir ou ajustar o conteúdo de um documento jurídico.
    """
    if not api_key:
        return "ERRO: Gemini API Key não configurada nas configurações do escritório."

    # Prompt rico com o contexto jurídico
    prompt = f"""
    Você é um assistente jurídico sênior especializado em redação de documentos.
    Sua tarefa é redigir o conteúdo para um documento jurídico baseado em um modelo base e instruções específicas.

    DADOS DO CLIENTE E CONTEXTO:
    {json.dumps(context, indent=2, ensure_ascii=False)}

    INSTRUÇÕES DO ADVOGADO:
    {instrucoes}

    MODELO BASE (Texto do Arquivo Original):
    ---
    {modelo_texto}
    ---

    REGRAS CRÍTICAS:
    1. SUBSTITUIÇÃO DE DADOS: Você DEVE substituir qualquer nome, CPF ou dado fictício que esteja no MODELO BASE pelos DADOS DO CLIENTE fornecidos acima.
    2. INSTRUÇÕES: Siga rigorosamente as instruções do advogado.
    3. RETORNO: Retorne APENAS o texto do documento redigido. Sem comentários, sem saudações.
    4. VARIÁVEIS: Se houver {{tags}} no modelo, preencha-as com os valores reais.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {'Content-Type': 'application/json'}

    # Tenta vários modelos em sequência e versões de API (Redundância Máxima)
    ultimo_erro = "Nenhum modelo disponível respondeu"
    for version in API_VERSIONS:
        for modelo in MODELOS_DISPONIVEIS:
            url = f"https://generativelanguage.googleapis.com/{version}/{modelo}:generateContent?key={api_key}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=40)
                if response.status_code == 200:
                    res_data = response.json()
                    if 'candidates' in res_data and len(res_data['candidates']) > 0:
                        return res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Se der erro 403 de chave vazada ou inválida, paramos o loop para avisar
                if response.status_code == 403:
                    return "ERRO 403: Acesso negado. Verifique se sua nova chave de API está correta e se o faturamento/projeto está ativo no Google Cloud."
                
                if response.status_code != 404: # Se for 404, apenas tentamos o próximo modelo/versão
                    err_msg = response.json().get("error", {}).get("message", "Erro desconhecido")
                    ultimo_erro = f"({response.status_code}) {err_msg}"
                
            except Exception as e:
                ultimo_erro = str(e)
                continue

    return f"Erro ao gerar conteúdo com IA após tentar vários modelos: {ultimo_erro}"

