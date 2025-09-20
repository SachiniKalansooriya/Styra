import requests
import json

BASE = 'http://127.0.0.1:8000'

# Test login to get a token
login_payload = {
    'email': 'jwt_test@example.com',
    'password': 'Test123'
}

print("=== Testing Full Authentication Flow ===")
login_resp = requests.post(BASE + '/auth/login', json=login_payload)
print('Login status:', login_resp.status_code)

if login_resp.status_code == 200:
    data = login_resp.json()
    access_token = data['access_token']
    print('✓ Got access_token')
    
    # Test API call with the token
    print("\n=== Testing /api/wardrobe/items ===")
    headers = {'Authorization': f'Bearer {access_token}'}
    api_resp = requests.get(BASE + '/api/wardrobe/items', headers=headers)
    print('API status:', api_resp.status_code)
    if api_resp.status_code == 200:
        print('✓ API call successful')
        print('Response:', api_resp.json())
    else:
        print('✗ API call failed')
        print('Status:', api_resp.status_code)
        try:
            print('Error response:', api_resp.json())
        except:
            print('Error text:', api_resp.text)
else:
    print('✗ Login failed:', login_resp.text)