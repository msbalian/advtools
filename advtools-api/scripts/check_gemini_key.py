import os, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("c:/projetosdev/advtools/.env"))
k = os.getenv("GEMINI_API_KEY", "").strip()
print(f"Key: {k[:8]}...{k[-4:]} (len={len(k)})")

# Testar se a chave lista modelos
r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={k}")
print(f"List models status: {r.status_code}")

if r.status_code == 200:
    for m in r.json().get("models", []):
        name = m["name"]
        if "flash" in name or "pro" in name:
            print(f"  OK: {name}")
else:
    print(r.text[:300])

# Testar chamada real com gemini-1.5-flash (quota separada)
print("\nTentando gemini-1.5-flash...")
payload = {"contents": [{"parts": [{"text": "Responda apenas: OK"}]}]}
for version in ["v1beta", "v1"]:
    for model in ["models/gemini-1.5-flash", "models/gemini-2.5-flash-preview-04-17"]:
        url = f"https://generativelanguage.googleapis.com/{version}/{model}:generateContent?key={k}"
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  {model} ({version}): {resp.status_code}")
        if resp.status_code == 200:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            print(f"    Resposta: {text}")
            break
        elif resp.status_code != 404:
            err = resp.json().get("error", {}).get("message", "")[:150]
            print(f"    Erro: {err}")
