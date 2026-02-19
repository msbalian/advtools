import sqlite3
import random

def popular_banco():
    conn = sqlite3.connect('primejud.db')
    cursor = conn.cursor()

    # Limpa dados antigos
    cursor.execute("DELETE FROM processos")
    cursor.execute("DELETE FROM leads")

    fases = ['Inicial', 'Instrução', 'Sentença', 'Recurso', 'Execução']
    tribunais = ['TJGO', 'TJSP', 'TRF1', 'TST']
    resultados = ['Ganho', 'Perdido', 'Ativo', 'Ativo'] # Mais ativos que finalizados

    print("🛠️ Gerando dados para BI...")

    # Gerar 30 processos fictícios
    for i in range(1, 31):
        num = f"500{random.randint(1000,9999)}2025809{random.randint(1000,9999)}"
        valor = random.randint(5000, 150000)
        dias_parado = random.randint(1, 45) # Alguns vão gerar alerta (>30)
        
        cursor.execute('''
            INSERT INTO processos (numero_processo, cliente_nome, tribunal, fase, valor_causa, status_interno, data_sem_movimentacao, ultima_movimentacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            num, 
            f"Cliente Exemplo {i}", 
            random.choice(tribunais),
            random.choice(fases),
            valor,
            random.choice(resultados),
            dias_parado,
            "Aguardando publicação de despacho..."
        ))

    # Gerar 10 Leads (CRM)
    origens = ['Google Ads', 'Instagram', 'Indicação']
    status_crm = ['Novo', 'Em Negociação', 'Fechado']
    
    for i in range(1, 11):
        cursor.execute("INSERT INTO leads (nome, telefone, origem, status) VALUES (?, ?, ?, ?)",
                       (f"Lead Interessado {i}", "(62) 99999-9999", random.choice(origens), random.choice(status_crm)))

    conn.commit()
    conn.close()
    print("✅ Dados fictícios gerados! O Dashboard vai ficar lindo.")

if __name__ == "__main__":
    popular_banco()