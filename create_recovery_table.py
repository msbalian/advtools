import sqlite3

DB_NAME = 'primejud_saas.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Criando tabela recuperacao_senha...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recuperacao_senha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expiracao DATETIME NOT NULL,
            usado BOOLEAN DEFAULT 0,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Tabela criada com sucesso!")

if __name__ == "__main__":
    create_table()
