import requests
import json

BASE = 'http://127.0.0.1:8000'

# Test signup
payload = {
    'name': 'jwt_test_user',
    'email': 'jwt_test@example.com',
    'password': 'Test123'
}

print("=== Testing Signup ===")
resp = requests.post(BASE + '/auth/signup', json=payload)
print('Signup status:', resp.status_code)
try:
    data = resp.json()
    print('Response keys:', list(data.keys()))
    if 'access_token' in data:
        print('✓ access_token returned')
        access_token = data['access_token']
        
        # Test API call with the token
        print("\n=== Testing API with JWT ===")
        headers = {'Authorization': f'Bearer {access_token}'}
        api_resp = requests.get(BASE + '/api/wardrobe/items', headers=headers)
        print('API status:', api_resp.status_code)
        if api_resp.status_code == 200:
            print('✓ API call successful with JWT')
        else:
            print('✗ API call failed:', api_resp.text)
    else:
        print('✗ no access_token')
    print(data)
except Exception as e:
    print('Error:', e)
    print(resp.text)
