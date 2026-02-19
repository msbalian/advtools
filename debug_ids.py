
import sqlite3

def check_ids():
    try:
        print("Iniciando check_ids...")
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        with open('d:/Projetos/advtools/debug_result.txt', 'w', encoding='utf-8') as f:
            f.write("-" * 30 + "\n")
            f.write("TIPOS DE SERVICO:\n")
            cursor.execute("SELECT id, nome, escritorio_id FROM tipos_servico")
            tipos = cursor.fetchall()
            for t in tipos:
                f.write(f"ID={t['id']} | Nome='{t['nome']}' | EscID={t['escritorio_id']}\n")
                
            f.write("\n" + "-" * 30 + "\n")
            f.write("USUARIOS:\n")
            cursor.execute("SELECT id, email, escritorio_id FROM usuarios")
            users = cursor.fetchall()
            for u in users:
                f.write(f"User='{u['email']}' | EscID={u['escritorio_id']}\n")
            f.write("-" * 30 + "\n")
            
        print("Arquivo debug_result.txt gerado com sucesso.")
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_ids()
