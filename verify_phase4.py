import ia_gemini
import os
from dotenv import load_dotenv

def verify_ai():
    print("🤖 Verificando Integração com Gemini...")
    load_dotenv()
    
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("❌ ERRO: Chave GEMINI_API_KEY não encontrada no .env")
        return

    print(f"🔑 Chave encontrada: {key[:5]}...")
    
    try:
        # Teste Simples
        resposta = ia_gemini.gerar_conteudo_juridico("Teste de Conexão", "Cliente Teste", "Apenas confirme que recebeu esta mensagem com um 'OK'.")
        
        if "Erro" in resposta:
             print(f"❌ Erro na API: {resposta}")
        else:
             print(f"✅ Sucesso! Resposta da IA: {resposta}")
             
    except Exception as e:
        print(f"❌ Exceção: {e}")

if __name__ == "__main__":
    verify_ai()
