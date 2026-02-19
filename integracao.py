import random
from datetime import datetime

class ControlJusAPI:
    """
    Classe simulada para integração com APIs Jurídicas (ControlJus/DataJud).
    Substitui a integração real para evitar erros de conexão durante o desenvolvimento.
    """
    
    def __init__(self):
        print("🔌 Módulo de Integração (ControlJus) Inicializado.")

    def buscar_recortes(self):
        """
        Simula a busca de novas publicações em Diários Oficiais.
        Retorna uma lista de recortes fictícios para teste.
        """
        # Simulação aleatória para não trazer sempre a mesma coisa
        if random.choice([True, False]):
            return [
                {
                    "texto": "Fica intimada a parte autora para se manifestar sobre a contestação e documentos juntados, no prazo legal. Processo em fase de instrução.",
                    "processoNumero": "5463708-33.2023.8.09.0100",
                    "dataDisponibilizacao": datetime.now().strftime("%d/%m/%Y")
                },
                {
                    "texto": "DECISÃO: Defiro o pedido de tutela de urgência para determinar a exclusão do nome do autor dos órgãos de proteção ao crédito.",
                    "processoNumero": "5002123-45.2024.8.09.0051",
                    "dataDisponibilizacao": datetime.now().strftime("%d/%m/%Y")
                }
            ]
        return []

    def pesquisar_acervo(self, termo):
        """
        Simula a pesquisa de jurisprudência ou processos por termo.
        """
        print(f"🔎 Buscando no acervo externo por: {termo}")
        
        # Retorna resultados simulados baseados no termo pesquisado
        return [
            {
                "titulo": f"Apelação Cível - Ação envolvendo {termo}",
                "resumo": f"EMENTA: APELAÇÃO CÍVEL. AÇÃO DE INDENIZAÇÃO. {termo.upper()}. DANO MORAL CONFIGURADO. QUANTUM MANTIDO. RECURSO DESPROVIDO.",
                "conteudo_completo": f"Vistos, relatados e discutidos... Acordam os integrantes da Turma Julgadora... Decisão sobre {termo}...",
                "data": "15/01/2025"
            },
            {
                "titulo": f"Agravo de Instrumento - Liminar sobre {termo}",
                "resumo": f"AGRAVO DE INSTRUMENTO. TUTELA DE URGÊNCIA. {termo.upper()}. REQUISITOS PREENCHIDOS. DECISÃO REFORMADA.",
                "conteudo_completo": "Relatório... Voto... Trata-se de agravo interposto contra decisão que indeferiu...",
                "data": "10/02/2025"
            }
        ]