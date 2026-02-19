from werkzeug.security import generate_password_hash
import sqlite3

try:
    conn = sqlite3.connect('primejud_saas.db')
    cursor = conn.cursor()
    
    # Check if user exists
    user = cursor.execute("SELECT id, email FROM usuarios WHERE email = 'admin@primejud.com'").fetchone()
    
    if user:
        print(f"Usuário encontrado: {user}")
        new_hash = generate_password_hash("123456")
        cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE email = 'admin@primejud.com'", (new_hash,))
        conn.commit()
        print("✅ SUCESSO: Senha de 'admin@primejud.com' alterada para '123456'")
    else:
        print("⚠️ ERRO: Usuário 'admin@primejud.com' NÃO encontrado.")
        # Create user if missing
        print("Criando usuário admin padrao...")
        new_hash = generate_password_hash("123456")
        cursor.execute("INSERT INTO usuarios (escritorio_id, nome, email, senha_hash, tipo, perfil) VALUES (1, 'Admin', 'admin@primejud.com', ?, 'Humano', 'Admin')", (new_hash,))
        conn.commit()
        print("✅ SUCESSO: Usuário criado e senha definida.")

    conn.close()
except Exception as e:
    print(f"❌ ERRO FATAL: {e}")
