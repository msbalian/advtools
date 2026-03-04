from sqlalchemy import create_engine, text
from config import Config

# Converte URL de asyncpg para sync pg se necessário (removendo +asyncpg)
DATABASE_URL = Config.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(DATABASE_URL)

def apply_migrations():
    with engine.begin() as conn:
        print("Adicionando colunas de assinatura em documentos_cliente...")
        try:
            conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN token_assinatura VARCHAR(32) UNIQUE;"))
            conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN status_assinatura VARCHAR(50) DEFAULT 'Aguardando';"))
            conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN hash_original VARCHAR(64);"))
            conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN hash_assinado VARCHAR(64);"))
            conn.execute(text("ALTER TABLE documentos_cliente ADD COLUMN token_validacao VARCHAR(32) UNIQUE;"))
        except Exception as e:
            print(f"Erro ao adicionar colunas na tabela (podem já existir): {e}")

if __name__ == "__main__":
    apply_migrations()
    print("Migrações de colunas concluídas. Tabelas novas serão criadas via create_tables.py")
