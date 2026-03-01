import google.generativeai as genai
import sys

def list_models(api_key):
    genai.configure(api_key=api_key)
    try:
        print("Modelos disponíveis:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Erro ao listar modelos: {e}")

if __name__ == "__main__":
    key = "AIzaSyBnByo-7buB_vs73vwLMmO-iUbeyEugaSI"
    list_models(key)
