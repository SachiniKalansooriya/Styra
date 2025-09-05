#!/usr/bin/env python3
"""
Debug script to test image analysis and see detailed results
"""

import os
import sys
from PIL import Image
import json
from services.free_ai_analyzer import free_ai_analyzer

def debug_image_analysis(image_path):
    """Debug image analysis for a specific image"""
    try:
        print(f"Analyzing image: {image_path}")
        print("=" * 50)
        
        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        print(f"Image size: {len(image_data)} bytes")
        
        # Load image for inspection
        image = Image.open(image_path)
        print(f"Image dimensions: {image.size}")
        print(f"Image mode: {image.mode}")
        
        # Analyze with our service
        result = free_ai_analyzer.analyze_clothing_item(image_data)
        
        print("\nAnalysis Results:")
        print("-" * 30)
        for key, value in result.items():
            if key == 'color_analysis' and isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    if sub_key == 'dominant_colors':
                        print(f"  {sub_key}: {sub_value[:3]}...")  # Show first 3 colors
                    else:
                        print(f"  {sub_key}: {sub_value}")
            elif key == 'category_analysis' and isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        
        # Let's also test the individual components
        print("\nDetailed Color Analysis:")
        print("-" * 30)
        image_pil = Image.open(image_path)
        if image_pil.mode != 'RGB':
            image_pil = image_pil.convert('RGB')
        
        # Get dominant colors
        dominant_colors = free_ai_analyzer._extract_dominant_colors(image_pil)
        print(f"Top 5 dominant colors (RGB): {dominant_colors[:5]}")
        
        # Get color name mapping
        color_name = free_ai_analyzer._map_color_to_name(dominant_colors)
        print(f"Detected color name: {color_name}")
        
        # Get category
        category = free_ai_analyzer._detect_category_enhanced(image_pil)
        print(f"Detected category: {category}")
        
        # Get features
        features = free_ai_analyzer._analyze_clothing_features(image_pil)
        print(f"Image features: {features}")
        
        return result
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python debug_image_analysis.py <image_path>")
        print("\nAvailable test images:")
        wardrobe_dir = "static/images/wardrobe"
        if os.path.exists(wardrobe_dir):
            for img in os.listdir(wardrobe_dir):
                if img.endswith(('.jpg', '.jpeg', '.png')):
                    print(f"  {wardrobe_dir}/{img}")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    debug_image_analysis(image_path)

if __name__ == "__main__":
    main()
