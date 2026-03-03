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


async def analisar_documento_para_organizacao(api_key: str, text_content: str = "", image_base64: str = "", mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """
    Analisa um documento (texto e/ou imagem) para fins de organização automática.
    Retorna JSON com categoria, nome sugerido e dados de despesa.
    """
    if not api_key:
        return {"categoria": "Outros", "nome_sugerido": "Documento sem Analise", "is_financeiro": False}

    prompt = """
    Analise o conteúdo deste documento jurídico ou financeiro e retorne um JSON estrito.
    Se for uma IMAGEM, descreva o que é (ex: Print de WhatsApp, Foto de RG, Nota Fiscal).
    Se for TEXTO, identifique o tipo de documento.

    ESTRUTURA DO JSON DE RETORNO:
    {
        "categoria": "Tipo de documento (ex: Procuração, RG/CPF, Comprovante de Residência, Despesa, Contrato, Petição)",
        "nome_sugerido": "Nome curto e limpo para o arquivo (ex: Procuracao_Assinada)",
        "is_financeiro": true/false,
        "valor": 0.0,
        "data": "YYYY-MM-DD ou null",
        "descricao": "Descrição curta se for financeiro"
    }

    REGRAS:
    1. Se for despesa (nota fiscal, recibo, boleto pago), is_financeiro deve ser true.
    2. O nome_sugerido não deve ter extensão (.pdf, .jpg).
    3. RETORNE APENAS O JSON.
    """

    content_parts = []
    if text_content:
        content_parts.append({"text": f"CONTEÚDO DO TEXTO:\n{text_content}"})
    if image_base64:
        content_parts.append({
            "inline_data": {
                "mime_type": mime_type or "image/jpeg",
                "data": image_base64
            }
        })
    
    content_parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": content_parts}]
    }
    headers = {'Content-Type': 'application/json'}

    # Tenta modelos que suportam Visão
    modelos_vision = ["models/gemini-1.5-flash", "models/gemini-1.5-pro"]
    
    for version in API_VERSIONS:
        for modelo in modelos_vision:
            url = f"https://generativelanguage.googleapis.com/{version}/{modelo}:generateContent?key={api_key}"
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=40)
                if response.status_code == 200:
                    res_data = response.json()
                    if 'candidates' in res_data and len(res_data['candidates']) > 0:
                        raw_text = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                        # Limpa possíveis markdown boxes ```json ... ```
                        json_str = raw_text.replace('```json', '').replace('```', '').strip()
                        try:
                            return json.loads(json_str)
                        except:
                            # Tenta extrair entre chaves se a IA falou algo extra
                            start = json_str.find('{')
                            end = json_str.rfind('}')
                            if start != -1 and end != -1:
                                return json.loads(json_str[start:end+1])
            except:
                continue

    return {"categoria": "Outros", "nome_sugerido": "Documento_Nao_Identificado", "is_financeiro": False}



