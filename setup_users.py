from werkzeug.security import generate_password_hash
import sqlite3

def fix_users():
    try:
        conn = sqlite3.connect('primejud_saas.db')
        
        # 1. Reset ADMIN
        print("--- Corrigindo ADMIN ---")
        admin_email = 'admin@primejud.com'
        senha_padrao = generate_password_hash("123456")
        
        # Check if admin exists
        cursor = conn.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,))
        if cursor.fetchone():
            conn.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_padrao, admin_email))
            print(f"✅ Senha do {admin_email} resetada para 123456")
        else:
            conn.execute("INSERT INTO usuarios (escritorio_id, nome, email, senha_hash, tipo, perfil) VALUES (1, 'Admin', ?, ?, 'Humano', 'Admin')", (admin_email, senha_padrao))
            print(f"✅ Usuário {admin_email} CRIADO com senha 123456")

        # 2. Create FERNANDO
        print("\n--- Criando FERNANDO ---")
        fernando_email = 'fernando@primejud.com.br' # Note o .br que vi no log
        
        cursor = conn.execute("SELECT id FROM usuarios WHERE email = ?", (fernando_email,))
        if cursor.fetchone():
            conn.execute("UPDATE usuarios SET senha_hash = ? WHERE email = ?", (senha_padrao, fernando_email))
            print(f"✅ Senha do {fernando_email} resetada para 123456")
        else:
            # Assumindo escritório ID 1. Se não existir, pega o primeiro.
            esc_id = conn.execute("SELECT id FROM escritorios LIMIT 1").fetchone()[0]
            conn.execute("INSERT INTO usuarios (escritorio_id, nome, email, senha_hash, tipo, perfil) VALUES (?, 'Fernando Cozac', ?, ?, 'Humano', 'Admin')", (esc_id, fernando_email, senha_padrao))
            print(f"✅ Usuário {fernando_email} CRIADO com senha 123456")
            
        conn.commit()
        conn.close()
        print("\nCONCLUSÃO: Tente logar agora!")
        
    except Exception as e:
        print(f"ERRO: {e}")

if __name__ == "__main__":
    fix_users()
