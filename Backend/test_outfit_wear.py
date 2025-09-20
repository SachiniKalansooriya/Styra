import requests
import json

BASE = 'http://127.0.0.1:8000'

# Test login first
login_payload = {
    'email': 'sach@gmail.com',
    'password': 'Sachini22'
}

print("=== Testing /api/outfit/wear endpoint ===")
login_resp = requests.post(BASE + '/auth/login', json=login_payload)
print('Login status:', login_resp.status_code)

if login_resp.status_code == 200:
    data = login_resp.json()
    access_token = data['access_token']
    print('✓ Got access_token')
    
    # Test the outfit wear endpoint with data similar to frontend
    print("\n=== Testing POST /api/outfit/wear ===")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    outfit_data = {
        "outfit_data": {
            "items": [
                {
                    "id": 1,
                    "name": "Test Item",
                    "category": "tops",
                    "color": "Blue",
                    "confidence": 0.85
                }
            ],
            "occasion": "casual",
            "confidence": 84,
            "generated_at": "2025-09-20T13:57:15.912Z",
            "total_items": 1
        },
        "user_id": 1,
        "occasion": "casual",
        "weather": "overcast clouds",
        "location": "Southern Province",
        "worn_date": "2025-09-20"
    }
    
    wear_resp = requests.post(BASE + '/api/outfit/wear', json=outfit_data, headers=headers)
    print('Outfit wear status:', wear_resp.status_code)
    if wear_resp.status_code == 200:
        print('✓ Outfit wear recorded successfully')
        print('Response:', wear_resp.json())
    else:
        print('✗ Outfit wear failed:', wear_resp.text)
        
else:
    print('✗ Login failed:', login_resp.text)