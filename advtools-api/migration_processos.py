import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from config import Config

async def migrate():
    engine = create_async_engine(Config.DATABASE_URL, echo=True)
    
    # 1. Tabelas
    async with engine.begin() as conn:
        print("Criando tabelas...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processos (
                id SERIAL PRIMARY KEY,
                escritorio_id INTEGER NOT NULL REFERENCES escritorios(id),
                cliente_id INTEGER REFERENCES clientes(id),
                advogado_responsavel_id INTEGER REFERENCES usuarios(id),
                numero_processo VARCHAR(50),
                tribunal VARCHAR(20),
                grau VARCHAR(5) DEFAULT 'G1',
                data_ajuizamento TIMESTAMP,
                nivel_sigilo INTEGER DEFAULT 0,
                classe_codigo INTEGER,
                classe_nome VARCHAR(255),
                orgao_julgador_codigo INTEGER,
                orgao_julgador_nome VARCHAR(255),
                orgao_julgador_municipio_ibge INTEGER,
                formato_codigo INTEGER,
                formato_nome VARCHAR(100) DEFAULT 'Eletrônico',
                sistema_codigo INTEGER,
                sistema_nome VARCHAR(100),
                titulo VARCHAR(255) NOT NULL,
                descricao TEXT,
                status VARCHAR(50) DEFAULT 'Ativo',
                prioridade VARCHAR(50) DEFAULT 'Normal',
                valor_causa FLOAT,
                area_direito VARCHAR(100),
                fase_processual VARCHAR(100),
                polo VARCHAR(50) DEFAULT 'Autor',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processo_partes (
                id SERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
                tipo_parte VARCHAR(100) NOT NULL,
                nome VARCHAR(255) NOT NULL,
                cpf_cnpj VARCHAR(50),
                tipo_pessoa VARCHAR(50) DEFAULT 'Física',
                advogado_nome VARCHAR(255),
                advogado_oab VARCHAR(50)
            );
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processo_assuntos (
                id SERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
                codigo_tpu INTEGER,
                nome VARCHAR(255) NOT NULL,
                principal BOOLEAN DEFAULT FALSE
            );
        """))

        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id SERIAL PRIMARY KEY,
                processo_id INTEGER NOT NULL REFERENCES processos(id) ON DELETE CASCADE,
                tipo VARCHAR(50) NOT NULL,
                codigo_movimento INTEGER,
                nome_movimento VARCHAR(255) NOT NULL,
                complementos_json TEXT,
                descricao TEXT,
                orgao_julgador_codigo INTEGER,
                orgao_julgador_nome VARCHAR(255),
                data_hora TIMESTAMP NOT NULL,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registrado_por_id INTEGER REFERENCES usuarios(id)
            );
        """))
        print("Tabelas criadas.")

    # 2. Colunas (Transações separadas para evitar quebra de bloco)
    async with engine.connect() as conn:
        print("Adicionando colunas às tabelas existentes...")
        for table, column, definition in [
            ("servicos", "processo_id", "INTEGER REFERENCES processos(id)"),
            ("pastas_documento", "processo_id", "INTEGER REFERENCES processos(id)")
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition};"))
                await conn.commit()
                print(f"Coluna '{column}' adicionada a '{table}'.")
            except Exception as e:
                await conn.rollback()
                print(f"Pulinado: Coluna '{column}' em '{table}' (Provavelmente já existe).")

    # 3. Índices
    async with engine.begin() as conn:
        print("Criando índices...")
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_processos_escritorio ON processos(escritorio_id);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_processos_cliente ON processos(cliente_id);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_processos_numero ON processos(numero_processo);"))
        print("Migração finalizada.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
