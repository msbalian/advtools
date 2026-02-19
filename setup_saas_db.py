import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = 'primejud_saas.db'

def setup_database():
    print(f"🔄 Iniciando configuração do banco de dados: {DB_NAME}")
    
    # Remove se existir para garantir schema novo (CUIDADO EM PRODUÇÃO)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("⚠️ Banco anterior removido para recriação limpa.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Tabela: Escritórios (Tenants)
    cursor.execute('''
    CREATE TABLE escritorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        documento TEXT, -- CPF ou CNPJ
        logo_path TEXT,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Tabela: Usuários
    cursor.execute('''
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        escritorio_id INTEGER,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        tipo TEXT DEFAULT 'Humano', -- Humano ou IA
        perfil TEXT DEFAULT 'Operacional', -- Admin, Comercial, Operacional
        FOREIGN KEY(escritorio_id) REFERENCES escritorios(id)
    )
    ''')

    # 3. Tabela: Tipos de Serviço
    cursor.execute('''
    CREATE TABLE tipos_servico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        escritorio_id INTEGER,
        nome TEXT NOT NULL,
        descricao_padrao TEXT,
        FOREIGN KEY(escritorio_id) REFERENCES escritorios(id)
    )
    ''')

    # 4. Tabela: Clientes
    cursor.execute('''
    CREATE TABLE clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        escritorio_id INTEGER,
        nome TEXT NOT NULL,
        documento TEXT, -- CPF/CNPJ
        telefone TEXT,
        email TEXT,
        endereco TEXT,
        data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(escritorio_id) REFERENCES escritorios(id)
    )
    ''')

    # 5. Tabela: Serviços Contratados (Financeiro)
    cursor.execute('''
    CREATE TABLE servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        escritorio_id INTEGER,
        cliente_id INTEGER,
        tipo_servico_id INTEGER,
        descricao TEXT,
        status TEXT DEFAULT 'Ativo',
        
        -- Dados Financeiros
        valor_total REAL,
        condicoes_pagamento TEXT, -- JSON com detalhes
        
        data_contratacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(escritorio_id) REFERENCES escritorios(id),
        FOREIGN KEY(cliente_id) REFERENCES clientes(id),
        FOREIGN KEY(tipo_servico_id) REFERENCES tipos_servico(id)
    )
    ''')

    # --- POPULANDO DADOS INICIAIS DE TESTE ---
    
    # Escritório Exemplo
    cursor.execute("INSERT INTO escritorios (nome, documento) VALUES (?, ?)", 
                   ("Escritório Modelo", "00.000.000/0001-00"))
    escritorio_id = cursor.lastrowid

    # Usuário Admin Padrão
    senha_hash = generate_password_hash("admin123")
    cursor.execute('''
        INSERT INTO usuarios (escritorio_id, nome, email, senha_hash, tipo, perfil)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (escritorio_id, "Admin", "admin@primejud.com", senha_hash, "Humano", "Admin"))
    
    # Tipos de Serviço Padrão
    tipos = ["Processo Judicial", "Processo Administrativo", "Assessoria", "Análise de Contrato", "Parecer"]
    for t in tipos:
        cursor.execute("INSERT INTO tipos_servico (escritorio_id, nome) VALUES (?, ?)", (escritorio_id, t))

    conn.commit()
    conn.close()
    print("✅ Banco de dados SAAS criado e populado com sucesso!")
    print(f"👉 Usuário Admin criado: admin@primejud.com / admin123")

if __name__ == "__main__":
    setup_database()
