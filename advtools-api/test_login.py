import requests
import time

def test_login():
    url = "http://localhost:8000/api/login"
    data = {
        "username": "contato@nubiacozacbalian.adv.br",
        "password": "123456" 
    }
    
    print(f"Testando POST {url}...")
    start = time.time()
    try:
        # Usamos timeout para não travar o script se o servidor travar
        response = requests.post(url, data=data, timeout=5)
        duration = time.time() - start
        print(f"Status: {response.status_code}")
        print(f"Duração: {duration:.2f}s")
        print(f"Resposta: {response.json()}")
    except requests.exceptions.Timeout:
        print("TEMPO ESGOTADO! O servidor não respondeu em 5 segundos.")
    except Exception as e:
        print(f"Erro ao testar login: {e}")

if __name__ == "__main__":
    test_login()
