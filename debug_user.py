
import sqlite3

def check_admin():
    try:
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Buscando usuarios...")
        cursor.execute("SELECT id, nome, email, escritorio_id FROM usuarios")
        users = cursor.fetchall()
        
        found = False
        for u in users:
            print(f"User: {u['nome']} ({u['email']}) - EscID: {u['escritorio_id']}")
            found = True
            
        if not found:
            print("Nenhum usuario encontrado.")
            
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_admin()
