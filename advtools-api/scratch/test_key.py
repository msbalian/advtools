env_key = "AIzaSyD804ONG6Tx0BVxtyRUghRetshlYq-a8ek"
placeholders = ["sua_chave", "your_key", "aqui", "insert_key", "api_key_gemini"]
is_placeholder = any(p in env_key.lower() for p in placeholders)
print(f"Is placeholder: {is_placeholder}")
for p in placeholders:
    if p in env_key.lower():
        print(f"Found: {p}")
