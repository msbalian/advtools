
import sqlite3

def migrate_db():
    try:
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        cursor = conn.cursor()
        
        print("Criando tabela pagamentos_contrato...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagamentos_contrato (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico_id INTEGER NOT NULL,
                tipo_pagamento TEXT,  -- Pix, Boleto, Dinheiro, etc.
                valor REAL,
                data_vencimento DATE,
                observacao TEXT,
                status TEXT DEFAULT 'Pendente', -- Pendente, Pago, Atrasado
                FOREIGN KEY(servico_id) REFERENCES servicos(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrate_db()
