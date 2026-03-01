import requests
import json

def list_models_rest(api_key):
    # Tenta v1 e v1beta
    versions = ["v1", "v1beta"]
    for v in versions:
        url = f"https://generativelanguage.googleapis.com/{v}/models?key={api_key}"
        try:
            print(f"\n--- Testando versão {v} ---")
            response = requests.get(url)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for m in models:
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        print(f"- {m.get('name')}")
            else:
                print(f"Erro {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    # O usuário não enviou a nova chave no chat (correto), 
    # mas eu posso tentar buscar do banco para testar se ele já configurou.
    # Como não tenho acesso direto ao banco via script simples aqui sem setup, 
    # vou pedir para o usuário rodar esse script ou eu mesmo tentar rodar 
    # se eu conseguir pegar a chave via crud/service.
    print("Script de diagnóstico pronto.")
