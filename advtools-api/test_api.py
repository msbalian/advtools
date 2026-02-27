import urllib.request
import json
import traceback

def test_register():
    data = {
        "nome": "New User",
        "email": "newuser@example.com",
        "senha": "password123",
        "escritorio_id": 1,
        "is_admin": True
    }
    
    req = urllib.request.Request(
        'http://localhost:8000/api/register',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        response = urllib.request.urlopen(req)
        print("Success:", response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}:")
        print(e.read().decode())
    except Exception as e:
        print("Other error:")
        traceback.print_exc()

test_register()
