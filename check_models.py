import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

def listar_modelos():
    if not API_KEY:
        print("❌ Sem chave API no .env")
        return

    # Endpoint que lista todos os modelos disponíveis
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            print("\n✅ MODELOS DISPONÍVEIS PARA SUA CHAVE:")
            print("="*40)
            for model in dados.get('models', []):
                # Filtra apenas modelos que geram texto (generateContent)
                if "generateContent" in model.get('supportedGenerationMethods', []):
                    print(f"👉 {model['name']}")
            print("="*40)
            print("\nCopie um desses nomes (ex: models/gemini-1.5-flash) para usar no ia_gemini.py")
        else:
            print(f"❌ Erro ao listar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    listar_modelos()