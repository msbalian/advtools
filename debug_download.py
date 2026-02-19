import sqlite3
import os

token = "62ec7ce8082646fe9fbfeada1517fec1"
conn = sqlite3.connect('primejud_saas.db')
conn.row_factory = sqlite3.Row

print(f"--- Debugging Token: {token} ---")

# 1. Check Signatario
sig = conn.execute("SELECT * FROM signatarios WHERE token_acesso = ?", (token,)).fetchone()
if not sig:
    print("❌ Token NOT FOUND in 'signatarios' table.")
else:
    print(f"✅ Token Found in 'signatarios'! ID: {sig['id']}, Doc ID: {sig['documento_id']}, Status: {sig['status']}")

# 1.5 Check Documentos (token_assinatura column?)
# First, let's see columns of documents
cursor = conn.execute("SELECT * FROM documentos LIMIT 1")
names = [description[0] for description in cursor.description]
print(f"Columns in 'documentos': {names}")

if 'token_assinatura' in names:
    doc_token = conn.execute("SELECT * FROM documentos WHERE token_assinatura = ?", (token,)).fetchone()
    if doc_token:
        print(f"✅ Token Found in 'documentos' (token_assinatura)! ID: {doc_token['id']}")
    else:
        print("❌ Token NOT FOUND in 'documentos' (token_assinatura).")
else:
    print("⚠️ Column 'token_assinatura' does NOT exist in 'documentos'.")

    
    # 2. Check Documento
    doc = conn.execute("SELECT * FROM documentos WHERE id = ?", (sig['documento_id'],)).fetchone()
    if not doc:
        print("❌ Documento NOT FOUND in 'documentos' table.")
    else:
        print(f"✅ Document Found! ID: {doc['id']}, Nome: {doc['nome_arquivo']}")
        print(f"📂 Caminho no Banco: '{doc['caminho_arquivo']}'")
        
        caminho = doc['caminho_arquivo']
        if caminho:
            # 3. Check File Existence
            # Test absolute and relative
            exists = os.path.exists(caminho)
            print(f"💿 File Exists (Direct): {exists}")
            
            if not exists:
                print(f"   Pwd: {os.getcwd()}")
                abs_path = os.path.abspath(caminho)
                print(f"   Abs Path: {abs_path}")
                print(f"   Join with cwd: {os.path.join(os.getcwd(), caminho)}")

conn.close()
