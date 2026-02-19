
import sqlite3

def seed_services():
    try:
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        cursor = conn.cursor()
        
        # Serviços Padrão
        servicos_padrao = [
            ("Consultoria Jurídica", "Análise e orientação verbal ou escrita."),
            ("Parecer Jurídico", "Documento técnico com opinião legal."),
            ("Contencioso Cível", "Atuação em processos judiciais cíveis."),
            ("Contencioso Trabalhista", "Atuação em processos trabalhistas."),
            ("Audiência", "Representação em audiência de instrução ou conciliação."),
            ("Elaboração de Contrato", "Minuta e revisão de instrumentos contratuais."),
            ("Diligência", "Cópias, despachos e protocolos presenciais."),
            ("Compliance", "Adequação às normas e regulamentos.")
        ]
        
        # Insere para o escritório ID 1 (Padrão) e ID 3 (Nubia - conforme logs anteriores)
        # Se quiser inserir para TODOS, teria que listar os escritórios.
        # Vamos inserir para o ID 1, que o sistema usa como fallback.
        
        print("Verificando serviços do Escritório Padrão (ID 1)...")
        existing = cursor.execute("SELECT count(*) FROM tipos_servico WHERE escritorio_id = 1").fetchone()[0]
        
        if existing < 3: # Se tiver poucos, popula
            print("Inserindo serviços padrão...")
            for nome, desc in servicos_padrao:
                try:
                    cursor.execute("INSERT INTO tipos_servico (escritorio_id, nome, descricao_padrao) VALUES (1, ?, ?)", (nome, desc))
                except sqlite3.IntegrityError:
                    pass # Já existe
            conn.commit()
            print("Serviços inseridos no ID 1.")
        else:
            print(f"Escritório 1 já possui {existing} serviços.")

        # Opcional: Inserir para o usuário atual se soubermos o ID dele.
        # Mas como a query agora pega (user OR ID=1), inserir no 1 já resolve para todos.
        
        conn.close()
        
    except Exception as e:
        print(f"Erro no seed: {e}")

if __name__ == "__main__":
    seed_services()
