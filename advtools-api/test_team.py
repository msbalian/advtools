import urllib.request
import json

try:
    req_login = urllib.request.Request(
        'http://localhost:8000/api/login',
        data=b'{"email":"newuser@example.com","senha":"password123"}',
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req_login) as res:
        token = json.loads(res.read())['access_token']
        
    req_add = urllib.request.Request(
        'http://localhost:8000/api/usuarios',
        data=b'{"nome":"Teste", "email":"teste@teste.com", "senha":"123", "tipo":"Humano", "perfil":"Colaborador", "ativo":true, "is_admin":false}',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'},
        method='POST'
    )
    with urllib.request.urlopen(req_add) as res:
        print("Success:", json.loads(res.read()))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
