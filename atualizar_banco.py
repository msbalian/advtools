import sqlite3

def atualizar_estrutura_banco():
    print("🛠️ Iniciando atualização do Banco de Dados ADVtools...")
    
    conn = sqlite3.connect('primejud.db')
    cursor = conn.cursor()
    
    # Lista das colunas novas que precisamos adicionar
    colunas_para_criar = [
        "ALTER TABLE processos ADD COLUMN cpf TEXT",
        "ALTER TABLE processos ADD COLUMN rg TEXT",
        "ALTER TABLE processos ADD COLUMN endereco TEXT",
        "ALTER TABLE processos ADD COLUMN profissao TEXT",
        "ALTER TABLE processos ADD COLUMN nacionalidade TEXT",
        "ALTER TABLE processos ADD COLUMN estado_civil TEXT"
    ]
    
    sucesso = 0
    ignorados = 0

    for comando in colunas_para_criar:
        try:
            cursor.execute(comando)
            print(f"✅ Sucesso: {comando}")
            sucesso += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️ Aviso: A coluna já existia (Ignorado).")
                ignorados += 1
            else:
                print(f"❌ Erro crítico ao executar: {comando} | {e}")

    conn.commit()
    conn.close()
    
    print(f"\n🏁 Atualização Finalizada! Criados: {sucesso} | Já existiam: {ignorados}")
    print("🚀 Agora seu banco suporta o CRM completo. Pode rodar o app.py!")

if __name__ == "__main__":
    atualizar_estrutura_banco()