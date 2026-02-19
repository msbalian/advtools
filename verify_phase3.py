import sqlite3

DB_NAME = 'primejud_saas.db'

def verify_phase3():
    print(f"🕵️ Verificando Fase 3 (CRM & Serviços)...")
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        
        # 1. Verifica Clientes
        conn.execute("INSERT INTO clientes (escritorio_id, nome, email) VALUES (1, 'Cliente Teste Script', 'teste@cli.com')")
        cli = conn.execute("SELECT * FROM clientes WHERE email='teste@cli.com'").fetchone()
        print(f"✅ Cliente criado: ID {cli['id']} - {cli['nome']}")
        
        # 2. Verifica Tipos de Serviço
        conn.execute("INSERT INTO tipos_servico (escritorio_id, nome) VALUES (1, 'Divórcio Express')")
        tipo = conn.execute("SELECT * FROM tipos_servico WHERE nome='Divórcio Express'").fetchone()
        print(f"✅ Tipo de Serviço criado: ID {tipo['id']} - {tipo['nome']}")
        
        # 3. Verifica Contrato
        conn.execute("INSERT INTO servicos (escritorio_id, cliente_id, tipo_servico_id, valor_total) VALUES (1, ?, ?, 1500.00)", (cli['id'], tipo['id']))
        contrato = conn.execute("SELECT * FROM servicos WHERE cliente_id=?", (cli['id'],)).fetchone()
        print(f"✅ Contrato criado: ID {contrato['id']} - Valor: {contrato['valor_total']}")
        
        # Limpeza
        conn.execute("DELETE FROM servicos WHERE id=?", (contrato['id'],))
        conn.execute("DELETE FROM tipos_servico WHERE id=?", (tipo['id'],))
        conn.execute("DELETE FROM clientes WHERE id=?", (cli['id'],))
        conn.commit()
        conn.close()
        
        print("\n🎉 Fase 3 Verificada com Sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro na verificação: {e}")

if __name__ == "__main__":
    verify_phase3()
