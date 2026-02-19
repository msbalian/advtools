
import sqlite3
conn = sqlite3.connect('primejud_saas.db')
cursor = conn.cursor()
tipos = cursor.execute("SELECT * FROM tipos_servico").fetchall()
print(f"Total tipos: {len(tipos)}")
for t in tipos:
    print(t)
conn.close()
