import sqlite3
from werkzeug.security import check_password_hash

DB_NAME = 'primejud_saas.db'

def verify():
    print(f"🕵️ Verificando banco de dados: {DB_NAME}")
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        
        # 1. Verifica Escritórios
        escritorios = conn.execute("SELECT * FROM escritorios").fetchall()
        print(f"✅ Escritórios encontrados: {len(escritorios)}")
        for e in escritorios:
            print(f"   - ID: {e['id']} | Nome: {e['nome']} | Doc: {e['documento']}")
            
        # 2. Verifica Usuários e Login
        usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
        print(f"✅ Usuários encontrados: {len(usuarios)}")
        
        admin = next((u for u in usuarios if u['email'] == 'admin@primejud.com'), None)
        if admin:
            if check_password_hash(admin['senha_hash'], 'admin123'):
                print("✅ Login Admin: SENHA CORRETA")
            else:
                print("❌ Login Admin: SENHA INCORRETA")
        else:
            print("❌ Usuário Admin não encontrado!")
            
        # 3. Verifica Tabelas Vazias (Métricas)
        clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
        servicos = conn.execute("SELECT COUNT(*) FROM servicos").fetchone()[0]
        print(f"✅ Clientes: {clientes} | Serviços: {servicos}")
        
        conn.close()
        print("\n🎉 Verificação concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro na verificação: {e}")

if __name__ == "__main__":
    verify()
