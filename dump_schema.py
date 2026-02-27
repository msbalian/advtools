import sqlite3

def dump_schema():
    conn = sqlite3.connect('primejud_saas.db')
    with open('schema_dump.txt', 'w', encoding='utf-8') as f:
        f.write("-- CLIENTES --\n")
        res = conn.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="clientes"').fetchone()
        if res: f.write(res[0] + "\n\n")
        
        f.write("-- SERVICOS --\n")
        res = conn.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="servicos"').fetchone()
        if res: f.write(res[0] + "\n\n")

if __name__ == '__main__':
    dump_schema()
