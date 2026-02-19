import sqlite3
conn = sqlite3.connect('primejud_saas.db')
conn.row_factory = sqlite3.Row
docs = conn.execute("SELECT id, nome_arquivo, status, token_validacao FROM documentos WHERE token_validacao IS NOT NULL AND token_validacao != '' LIMIT 5").fetchall()
for d in docs:
    print(f"ID:{d['id']} | {d['nome_arquivo']} | {d['status']} | token:{d['token_validacao']}")
if not docs:
    print("Nenhum documento com token de validacao encontrado")
conn.close()
