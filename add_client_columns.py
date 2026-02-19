import sqlite3
import os

DB_NAME = 'primejud_saas.db'

def fix_table():
    print("Iniciando correção da tabela clientes...")
    
    if not os.path.exists(DB_NAME):
        print(f"Erro: Banco de dados {DB_NAME} não encontrado.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    colunas_extras = [
        "data_nascimento", "nacionalidade", "estado_civil", "profissao", "rg", 
        "bairro", "cidade", "uf"
    ]
    
    for col in colunas_extras:
        try:
            print(f"Tentando adicionar coluna: {col}...")
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} TEXT")
            print(f" -> Sucesso: {col} adicionada.")
        except Exception as e:
            print(f" -> Aviso: {e}")
            
    conn.commit()
    conn.close()
    print("Processo concluído.")

if __name__ == "__main__":
    fix_table()
