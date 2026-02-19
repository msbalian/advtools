import sqlite3

def conectar():
    """Conecta ao banco de dados primejud.db"""
    return sqlite3.connect('primejud.db')

def inicializar_banco():
    """Cria as tabelas necessárias (ERP, BI e CRM)"""
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Processos (Completa para BI)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_processo TEXT UNIQUE NOT NULL,
            cliente_nome TEXT NOT NULL,
            tribunal TEXT,
            classe TEXT,
            ultima_movimentacao TEXT,
            data_hora_ultima_atualizacao TEXT,
            
            -- Novos Campos para o BI e Financeiro
            valor_causa REAL DEFAULT 0.0,
            honorarios_previstos REAL DEFAULT 0.0,
            fase TEXT DEFAULT 'Inicial',
            resultado_provavel TEXT,
            status_interno TEXT DEFAULT 'Ativo',
            data_sem_movimentacao INTEGER DEFAULT 0
        )
    ''')

    # 2. Tabela de CRM (Novos Clientes/Leads)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            origem TEXT,
            status TEXT DEFAULT 'Novo',
            data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Tabela de Signatários (ADVtools Sign)
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
    
    conn.commit()
    conn.close()
    print("✅ Banco de Dados (Estrutura Completa) pronto!")

def salvar_ou_atualizar_processo(dados):
    """
    Salva ou atualiza um processo vindo do DataJud ou do Cadastro Manual.
    Preserva dados financeiros se já existirem.
    """
    conn = conectar()
    cursor = conn.cursor()
    
    # Verifica se o processo já existe para não zerar o Valor da Causa se ele não vier na atualização
    valor_existente = 0.0
    try:
        cursor.execute("SELECT valor_causa FROM processos WHERE numero_processo = ?", (dados['numero'],))
        resultado = cursor.fetchone()
        if resultado:
            valor_existente = resultado[0]
    except:
        pass

    # Se veio valor novo no pacote, usa ele. Se não, mantém o antigo.
    valor_final = dados.get('valor_causa') if dados.get('valor_causa') else valor_existente

    cursor.execute('''
        INSERT INTO processos (
            numero_processo, cliente_nome, tribunal, classe, 
            ultima_movimentacao, data_hora_ultima_atualizacao, valor_causa
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(numero_processo) DO UPDATE SET
            cliente_nome = excluded.cliente_nome,
            classe = COALESCE(excluded.classe, processos.classe),
            ultima_movimentacao = excluded.ultima_movimentacao,
            data_hora_ultima_atualizacao = excluded.data_hora_ultima_atualizacao,
            valor_causa = excluded.valor_causa
    ''', (
        dados['numero'], 
        dados.get('cliente', 'Cliente Não Informado'), 
        dados['tribunal'],
        dados.get('classe'),
        dados.get('ultima_movimentacao'),
        dados.get('data_atualizacao'),
        valor_final
    ))
    
    conn.commit()
    conn.close()

def buscar_todos_processos():
    """Retorna lista simplificada para o loop de sincronização"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT numero_processo, tribunal, cliente_nome, ultima_movimentacao FROM processos')
    processos = cursor.fetchall()
    conn.close()
    return processos

if __name__ == "__main__":
    inicializar_banco()