import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MODELOS_DISPONIVEIS = [
    "gemini-2.5-flash",       # Prioridade 1: Disponível e rápido
    "gemini-flash-latest",    # Prioridade 2: Alias estável
    "gemini-2.0-flash-lite-001", # Prioridade 3: Versão leve
    "gemini-pro-latest"       # Fallback final
]

def gerar_conteudo_juridico(tipo_peca, nome_cliente, fatos_caso):
    """
    Função Híbrida:
    - Se for 'Procuração', gera os poderes.
    - Se for outra peça (ex: Petição Inicial), gera o texto completo (Fatos, Direito, Pedido).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "Erro: Sem chave API."

    # Verifica se é uma peça simples ou complexa
    if "procuração" in tipo_peca.lower():
        prompt = f"""
        Atue como advogado. Redija APENAS o parágrafo de PODERES ESPECÍFICOS para uma procuração.
        Cliente: {nome_cliente}. Caso: {fatos_caso}.
        """
    else:
        # Prompt para Peças Completas
        prompt = f"""
        Atue como um advogado sênior experiente.
        Redija o CORPO DE UMA {tipo_peca} completa.
        
        DADOS:
        - Cliente: {nome_cliente}
        - Fatos/Contexto: {fatos_caso}
        
        ESTRUTURA OBRIGATÓRIA (Use formatação Markdown simples ou texto corrido):
        1. DOS FATOS (Resuma o ocorrido com base no contexto, criando narrativa jurídica persuasiva).
        2. DO DIREITO (Cite artigos de lei, súmulas e doutrina aplicáveis ao caso).
        3. DOS PEDIDOS (Liste os pedidos formais pertinentes a essa peça).
        
        Não coloque cabeçalho nem endereçamento (o Word já tem). Comece direto no "I - DOS FATOS".
        """

    # Chamada padrão à API (Lógica de Loop que já criamos)
    for modelo in MODELOS_DISPONIVEIS: # Use sua lista global de modelos
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            print(f"Tentando modelo {modelo}...")
            response = requests.post(url, headers=headers, json=payload, timeout=90) # Timeout aumentado para 90s (peças longas)
            if response.status_code == 200:
                texto = response.json()['candidates'][0]['content']['parts'][0]['text']
                return texto.strip()
        except: continue

    return "Erro ao gerar conteúdo jurídico. Tente novamente."

def gerar_clausulas_contrato(tipo_servico, nome_cliente, detalhes_servico, valor, forma_pagamento):
    """
    Gera o objeto do contrato e cláusulas específicas com base no serviço.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "Erro: Sem chave API."

    prompt = f"""
    Atue como um advogado especialista em Contratos.
    Redija APENAS a CLÁUSULA DO OBJETO e a CLÁUSULA DE PAGAMENTO para um Contrato de Honorários/Prestação de Serviços.
    
    DADOS:
    - Cliente: {nome_cliente}
    - Tipo de Serviço: {tipo_servico}
    - Detalhes/Escopo: {detalhes_servico}
    - Valor Total: {valor}
    - Forma de Pagamento: {forma_pagamento}
    
    SAÍDA ESPERADA (Texto corrido, pronto para inserir no Word):
    
    DA CLÁUSULA PRIMEIRA - DO OBJETO
    (Descreva o serviço detalhadamente com base nos dados, com linguagem formal).
    
    DA CLÁUSULA SEGUNDA - DOS HONORÁRIOS E FORMA DE PAGAMENTO
    (Descreva o valor e como será pago, com base nos dados).
    
    Não coloque título do documento, apenas as cláusulas.
    """

    for modelo in MODELOS_DISPONIVEIS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                texto = response.json()['candidates'][0]['content']['parts'][0]['text']
                return texto.strip()
        except: continue

    return "Não foi possível gerar as cláusulas via IA."

def analisar_sentenca_ia(texto_pdf):
    """
    Envia o texto bruto da sentença para o Gemini extrair os pontos principais.
    Agora com sistema de redundância (tenta vários modelos).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "Erro: Chave não configurada."

    headers = {'Content-Type': 'application/json'}

    # Limitamos a 30.000 caracteres (aprox 15 pgs) para garantir que cabe no prompt
    # O Gemini Flash aguenta muito mais, mas isso economiza tempo de upload
    texto_seguro = texto_pdf[:30000]

    prompt = f"""
    Atue como um assistente jurídico sênior do escritório ADVtools. 
    Analise o texto da decisão judicial abaixo e gere um RESUMO ESTRATÉGICO.
    
    TEXTO DA DECISÃO (Excerto):
    {texto_seguro}

    SAÍDA ESPERADA (Use HTML básico para formatar com negrito <b>):
    
    1. <b>Resultado:</b> (Diga se foi Procedente, Improcedente ou Parcial)
    2. <b>Valores Envolvidos:</b> (Liste condenações, danos morais, honorários)
    3. <b>Prazos/Obrigações:</b> (Ex: 15 dias para pagamento, obrigação de fazer)
    4. <b>Recomendação:</b> (Sugira: Recorrer? Cumprir? Fazer acordo?)
    
    Seja técnico e direto.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    print("🧠 Advogado Robô lendo a sentença (PDF)...")

    # AQUI ESTÁ A MELHORIA: Usamos o loop também para o PDF
    for modelo in MODELOS_DISPONIVEIS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        
        try:
            # Timeout maior (20s) porque ler PDF demora mais que escrever um parágrafo
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                resultado = response.json()
                if 'candidates' in resultado and len(resultado['candidates']) > 0:
                    texto = resultado['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ Análise de PDF concluída com {modelo}")
                    return texto
            elif response.status_code == 404:
                continue
            
        except Exception as e:
            print(f"⚠️ Erro ao ler PDF com {modelo}: {e}")
            continue

    return "Não foi possível analisar a sentença. Todos os modelos de IA falharam ou estão ocupados."