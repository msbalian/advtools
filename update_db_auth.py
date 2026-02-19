
import sqlite3
from werkzeug.security import generate_password_hash

def migrate_auth():
    try:
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        cursor = conn.cursor()
        
        print("Adicionando colunas de autorização...")
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("Coluna is_admin adicionada.")
        except: print("Coluna is_admin já existe.")
        
        try:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN DEFAULT 0")
            print("Coluna ativo adicionada.")
        except: print("Coluna ativo já existe.")
        
        # Define todos os usuários atuais como ATIVOS para não bloquear ninguém antigo
        cursor.execute("UPDATE usuarios SET ativo = 1 WHERE ativo = 0 OR ativo IS NULL")
        
        # Define o Super Admin
        admin_email = "nandocozac@gmail.com"
        admin_pass = "Matheus10#"
        
        print(f"Configurando Super Admin: {admin_email}...")
        
        # Verifica se usuario existe
        user = cursor.execute("SELECT id FROM usuarios WHERE email = ?", (admin_email,)).fetchone()
        
        if user:
            # Atualiza permissões e senha (para garantir)
            new_hash = generate_password_hash(admin_pass)
            cursor.execute('''
                UPDATE usuarios 
                SET is_admin = 1, ativo = 1, senha_hash = ? 
                WHERE email = ?
            ''', (new_hash, admin_email))
            print("Super Admin atualizado com sucesso!")
        else:
            # Se não existir, cria (mas precisaria de escritorio_id etc, vamos assumir que existe pois ele disse que logou)
            print(f"ERRO: Usuário {admin_email} não encontrado no banco! Verifique se o email está correto.")
            
        conn.commit()
        conn.close()
        print("Migração de Auth concluída.")
        
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrate_auth()
