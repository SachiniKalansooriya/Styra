import requests
import json

BASE = 'http://127.0.0.1:8000'

# Test login
login_payload = {
    'email': 'sach@gmail.com',
    'password': 'Sachini22'
}

print("=== Testing Fixed Wardrobe API ===")
login_resp = requests.post(BASE + '/auth/login', json=login_payload)
print('Login status:', login_resp.status_code)

if login_resp.status_code == 200:
    data = login_resp.json()
    access_token = data['access_token']
    print('✓ Got access_token')
    
    # Test getting wardrobe items
    print("\n=== Testing GET /api/wardrobe/items ===")
    headers = {'Authorization': f'Bearer {access_token}'}
    api_resp = requests.get(BASE + '/api/wardrobe/items', headers=headers)
    print('API status:', api_resp.status_code)
    if api_resp.status_code == 200:
        print('✓ GET wardrobe items successful')
        result = api_resp.json()
        print('Items count:', len(result.get('items', [])))
    else:
        print('✗ GET failed:', api_resp.text)
    
    # Test adding a wardrobe item
    print("\n=== Testing POST /api/wardrobe/items ===")
    item_data = {
        'name': 'Test Item',
        'category': 'tops',
        'color': 'Blue',
        'season': 'all',
        'confidence': 0.85,
        'analysis_method': 'test'
    }
    
    post_resp = requests.post(BASE + '/api/wardrobe/items', json=item_data, headers=headers)
    print('POST status:', post_resp.status_code)
    if post_resp.status_code == 200:
        print('✓ POST wardrobe item successful')
        print('Response:', post_resp.json())
    else:
        print('✗ POST failed:', post_resp.text)
        
else:
    print('✗ Login failed:', login_resp.text)