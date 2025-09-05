# Backend/test_free_ai.py
import os
from services.free_ai_analyzer import free_ai_analyzer

def test_free_ai():
    """Test the free AI analyzer"""
    print("Testing Free AI Clothing Analyzer...")
    
    # Check service status
    status = free_ai_analyzer.get_service_status()
    print("Service Status:", status)
    
    # Test with a sample image (you need to provide this)
    test_image_path = "test_clothing.jpg"  # Replace with your test image
    
    if os.path.exists(test_image_path):
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
        
        print(f"Testing with image: {test_image_path}")
        result = free_ai_analyzer.analyze_clothing_item(image_data)
        
        print("Analysis Result:")
        print(f"Category: {result.get('suggestedCategory')}")
        print(f"Color: {result.get('suggestedColor')}")
        print(f"Confidence: {result.get('confidence'):.2f}")
        print(f"Method: {result.get('analysis_method')}")
        if 'description' in result:
            print(f"AI Description: {result['description']}")
        
    else:
        print(f"Test image not found: {test_image_path}")
        print("Please add a test image to test the analyzer")

if __name__ == "__main__":
    test_free_ai()