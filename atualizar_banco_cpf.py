import sqlite3

DB_NAME = 'primejud_saas.db'

def atualizar_banco():
    conn = sqlite3.connect(DB_NAME)
    try:
        conn.execute("ALTER TABLE signatarios ADD COLUMN cpf TEXT")
        print("Coluna 'cpf' adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        print(f"Erro/Aviso: {e} (Talvez a coluna já exista)")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    atualizar_banco()
