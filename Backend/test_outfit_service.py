#!/usr/bin/env python3
import os
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()

from services.enhanced_outfit_service import enhanced_outfit_service

def test_outfit_service():
    print('Testing wardrobe items retrieval...')
    items = enhanced_outfit_service.get_user_wardrobe_items(1)
    print(f'Found {len(items)} items')
    for item in items:
        print(f'- {item["name"]} ({item["category"]}) - {item["color"]}')

    print('\nTesting outfit generation...')
    weather_data = {
        'temperature': 22,
        'condition': 'partly cloudy',
        'humidity': 55,
        'windSpeed': 12,
        'precipitation': 0
    }

    try:
        outfit = enhanced_outfit_service.generate_outfit_recommendation(1, weather_data, 'casual')
        print('Outfit recommendation:')
        print(outfit)
    except Exception as e:
        print(f'Error generating outfit: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_outfit_service()
