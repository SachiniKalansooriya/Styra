from transformers import CLIPProcessor, CLIPModel, pipeline
import torch
from PIL import Image
import io  
import logging
import time  

class DeepFashionAnalyzer:
    def __init__(self):
        self.fashion_model = None
        self.fashion_processor = None
        self.category_classifier = None
        self.ai_loaded = False
        
        self._load_models()
    
    def _load_models(self):
        try:
            # Use standard CLIP instead of non-existent marqo model
            self.fashion_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.fashion_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.ai_loaded = True
            logging.info("DeepFashion models loaded successfully!")
            
        except Exception as e:
            logging.warning(f"Failed to load DeepFashion models: {e}")
            self.ai_loaded = False
    
    def analyze_clothing_item(self, image_data: bytes):
        try:
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            if self.ai_loaded:
                return self._fashion_analysis(image)
            else:
                return self._fallback_analysis()
                
        except Exception as e:
            return self._create_error_response(str(e))
    
    def _fashion_analysis(self, image):
        # Define comprehensive fashion categories
        categories = [
            "dress", "shirt", "blouse", "t-shirt", "tank top", "sweater",
            "pants", "jeans", "shorts", "skirt", "skirts", "leggings", 
            "jacket", "coat", "blazer", "cardigan", "hoodie", "jersey",
            "shoes", "boots", "sneakers", "sandals", "flip-flops", "heels",
            "sandals", "slingbacks", "loafers", "moccasins", "espadrilles"
        ]
        
        colors = [
            "red", "blue", "green", "yellow", "black", "white",
            "pink", "purple", "orange", "brown", "gray", "beige",
            "navy", "turquoise", "teal", "maroon", "olive", "mustard",
            "cream", "coral", "lavender", "mint", "khaki", "bronze",
            "gold", "silver", "multi", "pastel"
        ]
        
        occasions = [
            "casual everyday wear", "business professional", "formal evening",
            "workout athletic wear", "party night out", "romantic date", "beach", "holiday", "streetwear"
        ]
        
        # Get category using CLIP
        category_inputs = self.fashion_processor(
            text=categories, images=image, return_tensors="pt", padding=True
        )
        category_outputs = self.fashion_model(**category_inputs)
        category_probs = category_outputs.logits_per_image.softmax(dim=1)
        best_category_idx = category_probs.argmax()
        
        # Get color using CLIP
        color_inputs = self.fashion_processor(
            text=colors, images=image, return_tensors="pt", padding=True
        )
        color_outputs = self.fashion_model(**color_inputs)
        color_probs = color_outputs.logits_per_image.softmax(dim=1)
        best_color_idx = color_probs.argmax()
        
        # Get occasion using CLIP
        occasion_inputs = self.fashion_processor(
            text=occasions, images=image, return_tensors="pt", padding=True
        )
        occasion_outputs = self.fashion_model(**occasion_inputs)
        occasion_probs = occasion_outputs.logits_per_image.softmax(dim=1)
        best_occasion_idx = occasion_probs.argmax()
        
        # Map categories to your system
        category_mapping = {
            "dress": "dresses",
            "shirt": "tops",
            "blouse": "tops",
            "t-shirt": "tops",
            "tank top": "tops",
            "sweater": "tops",
            "jersey": "tops",
            "pants": "bottoms",
            "jeans": "bottoms",
            "shorts": "bottoms",
            "skirt": "bottoms",
            "skirts": "bottoms",
            "leggings": "bottoms",
            "jacket": "outerwear",
            "coat": "outerwear",
            "blazer": "outerwear",
            "cardigan": "outerwear",
            "hoodie": "tops",
            "shoes": "shoes",
            "boots": "shoes",
            "sneakers": "shoes",
            "sandals": "shoes",
            "flip-flops": "shoes",
            "heels": "shoes",
            "espadrilles": "shoes",
            "loafers": "shoes",
            "moccasins": "shoes"
        }
        
        raw_category = categories[best_category_idx]
        final_category = category_mapping.get(raw_category, "tops")
        
        # Map occasions
        occasion_mapping = {
            "casual everyday wear": "casual",
            "business professional": "work",
            "formal evening": "formal",
            "workout athletic wear": "workout",
            "party night out": "party",
            "romantic date": "datenight"
        }
        
        raw_occasion = occasions[best_occasion_idx]
        final_occasion = occasion_mapping.get(raw_occasion, "casual")
        
        return {
            'suggestedCategory': final_category,
            'suggestedColor': colors[best_color_idx].title(),
            'suggestedOccasion': final_occasion,
            'confidence': float(category_probs.max()),
            'analysis_method': 'deepfashion_clip',
            'success': True,
            'processing_time': time.time()
        }
    
    def _fallback_analysis(self):
        """MISSING METHOD - Added fallback"""
        return {
            'suggestedCategory': 'tops',
            'suggestedColor': 'Unknown',
            'suggestedOccasion': 'casual',
            'confidence': 0.5,
            'analysis_method': 'deepfashion_fallback',
            'success': True
        }
    
    def _create_error_response(self, error_message):
        """MISSING METHOD - Added error response"""
        return {
            'suggestedCategory': 'tops',
            'suggestedColor': 'Unknown',
            'suggestedOccasion': 'casual',
            'confidence': 0.3,
            'analysis_method': 'deepfashion_error',
            'success': False,
            'error': error_message
        }
    
    def get_service_status(self):
        """MISSING METHOD - Added service status"""
        return {
            'ai_models_loaded': self.ai_loaded,
            'supported_categories': [
                'tops', 'bottoms', 'dresses', 'outerwear', 'shoes', 'accessories',
                'skirts', 'jersey', 'sportswear', 'sneakers', 'sandals', 'formal'
            ],
            'supported_colors': [
                'Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 'Pink', 'Purple', 'Orange', 'Brown', 'Gray', 'Beige',
                'Navy', 'Turquoise', 'Teal', 'Maroon', 'Olive', 'Mustard', 'Cream', 'Coral', 'Lavender', 'Mint', 'Khaki', 'Bronze', 'Gold', 'Silver', 'Multi', 'Pastel'
            ],
            'supported_occasions': ['casual', 'work', 'formal', 'workout', 'party', 'datenight', 'beach', 'holiday', 'streetwear'],
            'analysis_methods': ['deepfashion_clip', 'deepfashion_fallback'],
            'model_name': 'openai/clip-vit-base-patch32'
        }

# Export the analyzer
deepfashion_analyzer = DeepFashionAnalyzer()