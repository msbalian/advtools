import asyncio
import httpx

async def test_file_manager():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # 1. Login
        print("Testando Login...")
        login_res = await client.post("/api/token", data={
            "username": "contato@nubiacozacbalian.adv.br",
            "password": "piabanha"
        })
        if login_res.status_code != 200:
            print("Falha no login!")
            return
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Testar Listagem de Clientes (Pastas Virtuais)
        print("Testando Listagem de Clientes...")
        clientes_res = await client.get("/api/clientes", headers=headers)
        if clientes_res.status_code == 200:
            print(f"Sucesso: {len(clientes_res.json())} clientes encontrados.")

        # 3. Testar Filtro de Modelos no Escritório
        print("Testando Filtro de Modelos...")
        # Simula o que o FileExplorer faz: /api/documentos/escritorio?tags=modelo
        # Nota: Precisamos ver se o endpoint de documentos suporta tags ou se filtramos no front.
        # No código atual do FileExplorer.vue, filtramos Docs por .docx se o título for 'Modelos'
        modelos_res = await client.get("/api/documentos/escritorio", headers=headers)
        if modelos_res.status_code == 200:
            docs = modelos_res.json()
            docx_only = [d for d in docs if d['arquivo_path'].lower().endswith('.docx')]
            print(f"Sucesso: {len(docs)} documentos internos, {len(docx_only)} são .docx (modelos).")

        # 4. Testar Listagem Global (arquivos.py)
        print("Testando Listagem Global...")
        global_res = await client.get("/api/arquivos/list?tipo=modelos", headers=headers)
        if global_res.status_code == 200:
             print(f"Sucesso (Global): {len(global_res.json())} modelos encontrados.")

if __name__ == "__main__":
    asyncio.run(test_file_manager())
