
import sqlite3

def check_tipos():
    try:
        conn = sqlite3.connect('d:/Projetos/advtools/primejud_saas.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipos_servico")
        rows = cursor.fetchall()
        print(f"Total tipos: {len(rows)}")
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_tipos()
