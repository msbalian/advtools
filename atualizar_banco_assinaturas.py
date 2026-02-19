import sqlite3
import os

DB_NAME = 'primejud_saas.db'

def migrar_banco():
    print(f"Iniciando migração para ADVtools Sign e Banco: {DB_NAME}...")
    
    if not os.path.exists(DB_NAME):
        print("Banco de dados não encontrado. Execute o app primeiro para criar.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Tabela de Signatários
    print("Criando tabela 'signatarios'...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signatarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento_id INTEGER NOT NULL,
            token_acesso TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            funcao TEXT DEFAULT 'Parte',
            
            status TEXT DEFAULT 'Pendente',
            data_visualizacao DATETIME,
            data_assinatura DATETIME,
            
            ip_assinatura TEXT,
            user_agent_assinatura TEXT,
            imagem_assinatura_path TEXT,
            
            FOREIGN KEY(documento_id) REFERENCES documentos(id)
        )
    ''')
    
    # 2. Atualizar Tabela Documentos
    print("Atualizando tabela 'documentos'...")
    try:
        cursor.execute("ALTER TABLE documentos ADD COLUMN hash_original TEXT")
    except Exception as e:
        print(f"Col hash_original: {e}")

    try:
        cursor.execute("ALTER TABLE documentos ADD COLUMN hash_assinado TEXT")
    except Exception as e:
        print(f"Col hash_assinado: {e}")
        
    try:
        # Garante que status_externo exista (reutilizando para status do envelope)
        cursor.execute("ALTER TABLE documentos ADD COLUMN status_env TEXT DEFAULT 'Aberto'")
    except Exception as e:
        print(f"Col status_env: {e}")

    conn.commit()
    conn.close()
    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    migrar_banco()
