import requests
import os
import sys
from datetime import datetime, timedelta

# Import jwt helper from the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.jwt_utils import create_access_token

BASE = os.getenv('BACKEND_URL', 'http://localhost:8000')

# Create a test token for user id 1
payload = {'sub': '1', 'email': 'test@example.com'}
access_token = create_access_token(payload, expires_delta=timedelta(minutes=30))

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

sample = {
    'outfit_data': {
        'items': [
            {'id': 1, 'name': 'Gray sweater', 'category': 'tops', 'color': 'gray', 'image_url': None, 'confidence': 82},
            {'id': 2, 'name': 'Gray office trousers', 'category': 'bottoms', 'color': 'gray', 'image_url': None, 'confidence': 80}
        ],
        'occasion': 'work',
        'confidence': 82
    },
    'occasion': 'work',
    'weather': {'temperature': 28, 'condition': 'sunny'},
    'location': {'latitude': 6.9, 'longitude': 79.8},
    'worn_date': datetime.now().date().isoformat()
}

print('Posting to', BASE + '/api/outfit/wear')
r = requests.post(BASE + '/api/outfit/wear', json=sample, headers=headers, timeout=10)
print('Status', r.status_code)
print('Response', r.text)
