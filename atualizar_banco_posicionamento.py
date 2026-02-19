import sqlite3
import os

DB_PATH = 'primejud_saas.db'

def adicionar_colunas_posicionamento():
    if not os.path.exists(DB_PATH):
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    colunas = [
        ("page_number", "INTEGER"),
        ("x_pos", "REAL"),
        ("y_pos", "REAL"),
        ("width", "REAL"),
        ("height", "REAL")
    ]

    tabela = "signatarios"
    
    # Verifica colunas existentes
    cursor.execute(f"PRAGMA table_info({tabela})")
    existentes = [col[1] for col in cursor.fetchall()]

    alteracoes = 0
    for col_nome, col_tipo in colunas:
        if col_nome not in existentes:
            try:
                print(f"Adicionando coluna '{col_nome}' na tabela '{tabela}'...")
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {col_nome} {col_tipo}")
                alteracoes += 1
            except sqlite3.OperationalError as e:
                print(f"Erro ao adicionar '{col_nome}': {e}")
        else:
            print(f"Coluna '{col_nome}' já existe.")

    if alteracoes > 0:
        conn.commit()
        print(f"Sucesso! {alteracoes} colunas adicionadas.")
    else:
        print("Nenhuma alteração necessária.")

    conn.close()

if __name__ == "__main__":
    adicionar_colunas_posicionamento()
