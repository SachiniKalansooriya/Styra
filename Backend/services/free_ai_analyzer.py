# Backend/services/free_ai_analyzer.py
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image, ImageEnhance
import torch
import cv2
import numpy as np
import io
import logging
from typing import Dict, Any, Tuple, List
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreeAIClothingAnalyzer:
    def __init__(self):
        """Initialize the free AI analyzer with Hugging Face models"""
        self.ai_loaded = False
        self.processor = None
        self.model = None
        
        # Category and color mappings - EXPANDED
        self.category_keywords = {
            'dresses': ['dress', 'gown', 'frock', 'sundress', 'maxi', 'midi', 'mini dress', 'evening dress', 
                      'cocktail dress', 'slip dress', 'sheath dress', 'a-line dress', 'shift dress'],
            'tops': ['shirt', 'blouse', 'top', 'tee', 't-shirt', 'sweater', 'hoodie', 'tank', 'polo', 
                   'sweatshirt', 'turtleneck', 'crop top', 'tunic', 'camisole', 'button-up', 'button-down',
                   'sleeveless', 'jersey', 'henley', 'vneck', 'crewneck'],
            'bottoms': ['pants', 'jeans', 'trousers', 'shorts', 'skirt', 'leggings', 'slacks', 'chinos',
                       'joggers', 'culottes', 'corduroys', 'cargo pants', 'khakis', 'palazzo pants',
                       'mini skirt', 'maxi skirt', 'pencil skirt', 'pleated skirt', 'denim skirt'],
            'shoes': ['shoes', 'boots', 'sneakers', 'sandals', 'heels', 'flats', 'loafers', 'pumps',
                    'oxfords', 'mules', 'espadrilles', 'ankle boots', 'running shoes', 'slippers',
                    'flip flops', 'wedges', 'stilettos', 'platforms', 'combat boots', 'hiking boots'],
            'accessories': ['bag', 'purse', 'hat', 'cap', 'jewelry', 'belt', 'watch', 'scarf', 'handbag',
                          'backpack', 'tote', 'crossbody', 'clutch', 'wallet', 'sunglasses', 'gloves',
                          'beanie', 'fedora', 'bracelet', 'earrings', 'necklace', 'ring', 'socks',
                          'tie', 'bow tie', 'headband', 'hair clip', 'brooch', 'pin', 'cufflinks'],
            'outerwear': ['jacket', 'coat', 'blazer', 'cardigan', 'vest', 'windbreaker', 'parka',
                        'raincoat', 'trench coat', 'puffer jacket', 'fleece', 'bomber jacket',
                        'denim jacket', 'leather jacket', 'peacoat', 'poncho', 'shacket', 'overcoat'],
            'sportswear': ['tracksuit', 'sweatpants', 'sports bra', 'cycling shorts', 'workout top',
                         'running tights', 'gym shorts', 'yoga pants', 'rashguard', 'swimsuit',
                         'swim trunks', 'athletic wear', 'jersey', 'ski jacket', 'hiking pants'],
            'formal': ['suit', 'tuxedo', 'formal dress', 'evening gown', 'ball gown', 'cocktail dress',
                     'three piece suit', 'formal shirt', 'dress pants', 'cummerbund'],
            'sleepwear': ['pajamas', 'nightgown', 'robe', 'slippers', 'nightshirt', 'sleep mask',
                        'sleeping robe', 'loungewear', 'nightwear', 'pjs'],
            'underwear': ['bra', 'underwear', 'boxers', 'briefs', 'panties', 'lingerie', 'shapewear',
                        'undershirt', 'camisole', 'slip', 'bodysuit']
        }
        
        # Expanded color keywords
        self.color_keywords = {
            'Red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon', 'cherry', 'ruby', 'wine', 'cardinal'],
            'Blue': ['blue', 'navy', 'azure', 'cobalt', 'royal blue', 'sapphire', 'sky blue', 'turquoise', 
                   'teal', 'cyan', 'indigo', 'periwinkle', 'cornflower', 'midnight blue', 'denim'],
            'Green': ['green', 'olive', 'mint', 'emerald', 'forest', 'lime', 'sage', 'hunter green',
                    'avocado', 'seafoam', 'jade', 'moss', 'chartreuse', 'kelly green'],
            'Yellow': ['yellow', 'gold', 'amber', 'lemon', 'mustard', 'canary', 'sunshine', 'banana',
                     'flaxen', 'honey', 'butterscotch', 'goldenrod'],
            'Pink': ['pink', 'rose', 'magenta', 'fuchsia', 'coral', 'salmon', 'blush', 'bubblegum',
                   'watermelon', 'flamingo', 'dusty rose', 'hot pink', 'baby pink'],
            'Purple': ['purple', 'violet', 'lavender', 'plum', 'indigo', 'lilac', 'mauve', 'amethyst',
                     'periwinkle', 'grape', 'orchid', 'heliotrope', 'mulberry'],
            'Orange': ['orange', 'peach', 'tangerine', 'burnt orange', 'apricot', 'pumpkin', 'persimmon',
                     'rust', 'copper', 'terracotta', 'carrot', 'coral'],
            'Brown': ['brown', 'tan', 'beige', 'khaki', 'chocolate', 'camel', 'coffee', 'mocha', 'taupe',
                    'chestnut', 'umber', 'mahogany', 'sepia', 'bronze', 'hazel', 'sienna'],
            'Black': ['black', 'dark', 'charcoal', 'ebony', 'midnight', 'onyx', 'jet', 'raven'],
            'White': ['white', 'cream', 'ivory', 'off-white', 'pearl', 'snow', 'eggshell', 'alabaster',
                    'bone', 'vanilla', 'chalk', 'linen'],
            'Gray': ['gray', 'grey', 'silver', 'slate', 'ash', 'charcoal', 'dove', 'pewter', 'platinum',
                   'smoke', 'graphite', 'stone', 'cement', 'heather'],
            'Multicolor': ['multicolor', 'multicolored', 'colorful', 'rainbow', 'patterned', 'variegated',
                         'tie-dye', 'printed', 'floral', 'striped', 'polka dot', 'plaid', 'paisley'],
            'Metallic': ['metallic', 'gold', 'silver', 'bronze', 'copper', 'chrome', 'platinum', 'brass'],
            'Pastel': ['pastel', 'light', 'soft', 'baby blue', 'baby pink', 'mint', 'lavender', 'peach']
        }
        
        # Places to wear / occasions
        self.occasion_keywords = {
            'casual': ['everyday', 'casual', 'daily', 'relaxed', 'lounging', 'weekend', 'around town', 
                     'errands', 'informal', 'laid-back', 'street style'],
            'formal': ['formal', 'elegant', 'fancy', 'sophisticated', 'dressy', 'black tie', 'gala', 
                     'ceremony', 'wedding', 'cocktail', 'upscale', 'evening'],
            'business': ['office', 'work', 'professional', 'business', 'corporate', 'meeting', 'presentation', 
                       'interview', 'workplace', 'business casual'],
            'athletic': ['gym', 'workout', 'exercise', 'sports', 'fitness', 'running', 'training', 'yoga', 
                       'athletic', 'jogging', 'hiking', 'outdoor activities'],
            'beachwear': ['beach', 'pool', 'swim', 'swimming', 'resort', 'vacation', 'tropical', 'cruise', 
                        'sunbathing', 'waterside'],
            'party': ['party', 'club', 'nightout', 'celebration', 'festive', 'dance', 'nightclub', 
                    'birthday', 'entertainment', 'social event'],
            'datenight': ['date', 'romantic', 'dinner', 'night out', 'restaurant', 'special occasion'],
            'seasonal': ['winter', 'summer', 'spring', 'fall', 'autumn', 'holiday', 'christmas', 
                       'thanksgiving', 'halloween', 'seasonal']
        }
        
        # Try to load AI models
        self._load_ai_models()
    
    def _load_ai_models(self):
        """Load Hugging Face models for AI analysis"""
        try:
            logger.info("Loading free AI models (this may take a moment on first run)...")
            
            # Load BLIP model for image captioning
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            
            # Set to evaluation mode
            self.model.eval()
            
            self.ai_loaded = True
            logger.info("Free AI models loaded successfully!")
            
        except Exception as e:
            logger.warning(f"Could not load AI models: {e}")
            logger.info("Will use rule-based analysis instead")
            self.ai_loaded = False
    
    def analyze_clothing_item(self, image_data: bytes) -> Dict[str, Any]:
        """Main analysis method with AI and fallback options"""
        start_time = time.time()
        
        try:
            # Validate and preprocess image
            image = self._preprocess_image(image_data)
            if image is None:
                return self._create_error_response("Invalid image data")
            
            # Try AI analysis first
            if self.ai_loaded:
                ai_result = self._ai_analysis(image)
                if ai_result and ai_result.get('confidence', 0) > 0.6:
                    ai_result['processing_time'] = time.time() - start_time
                    return ai_result
            
            # Fallback to enhanced rule-based analysis
            rule_result = self._enhanced_rule_analysis(image)
            rule_result['processing_time'] = time.time() - start_time
            return rule_result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._create_error_response(str(e))
    
    def _preprocess_image(self, image_data: bytes) -> Image.Image:
        """Preprocess image for analysis"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (for performance)
            max_size = 800
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def _ai_analysis(self, image: Image.Image) -> Dict[str, Any]:
        """AI-powered analysis using Hugging Face BLIP model"""
        try:
            logger.info("Running AI analysis with Hugging Face BLIP model...")
            
            # Generate image description using BLIP
            inputs = self.processor(image, return_tensors="pt")
            
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=50)
                description = self.processor.decode(out[0], skip_special_tokens=True)
            
            logger.info(f"AI generated description: {description}")
            
            # Extract category from description
            category, cat_confidence = self._extract_category_from_description(description)
            
            # Extract color from description and image
            color = self._extract_color_from_description(description)
            if color == 'Unknown':
                color = self._analyze_dominant_color(image)
                
            # Extract occasion from description
            occasion = self._extract_occasion_from_description(description)
            
            # Calculate overall confidence
            confidence = min(cat_confidence + 0.2, 0.95)  # AI gets confidence boost
            
            result = {
                'suggestedCategory': category,
                'suggestedColor': color,
                'suggestedOccasion': occasion,  # Always include occasion
                'confidence': confidence,
                'analysis_method': 'free_huggingface_ai',
                'ai_description': description,
                'features': {
                    'ai_description': description,
                    'model_used': 'Salesforce/blip-image-captioning-base',
                    'occasion': occasion  # Always include occasion in features
                },
                'detected_colors': [color],
                'success': True
            }
                
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _extract_category_from_description(self, description: str) -> Tuple[str, float]:
        """Extract clothing category from AI description"""
        description_lower = description.lower()
        
        # Check for direct category keywords in description
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category, 0.85
        
        # More sophisticated analysis if no direct match
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                # Check for partial matches
                keyword_parts = keyword.lower().split()
                for part in keyword_parts:
                    if len(part) > 3 and part in description_lower:
                        score += 0.15
            
            # Add context-based scores
            if category == 'tops' and any(w in description_lower for w in ['shirt', 'wearing', 'top']):
                score += 0.2
            elif category == 'dresses' and any(w in description_lower for w in ['woman', 'wearing', 'dress']):
                score += 0.2
            elif category == 'formal' and any(w in description_lower for w in ['formal', 'suit', 'elegant']):
                score += 0.2
            elif category == 'sportswear' and any(w in description_lower for w in ['sport', 'athletic', 'workout']):
                score += 0.2
                
            category_scores[category] = score
        
        # Get best scoring category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                return best_category[0], min(0.5 + best_category[1], 0.85)
        
        # Default based on common words
        if any(word in description_lower for word in ['wearing', 'person', 'man', 'woman']):
            return 'tops', 0.6
        
        return 'tops', 0.4
    
    def _extract_color_from_description(self, description: str) -> str:
        """Extract color from AI description"""
        description_lower = description.lower()
        
        # Check for direct color keywords in description
        for color, keywords in self.color_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return color
        
        # Check for compound colors
        color_words = re.findall(r'(?:dark|light|pale|bright|deep)\s+(\w+)', description_lower)
        for color_word in color_words:
            for color, keywords in self.color_keywords.items():
                if color_word in [k.lower() for k in keywords]:
                    return color
        
        # Check for generic color descriptions
        if any(word in description_lower for word in ['colorful', 'multi-colored', 'multicolor', 'patterned']):
            return 'Multicolor'
        elif any(word in description_lower for word in ['dark colored', 'dark tone', 'black']):
            return 'Black'
        elif any(word in description_lower for word in ['light colored', 'white', 'pale']):
            return 'White'
        
        return 'Unknown'
    
    def _extract_occasion_from_description(self, description: str) -> str:
        """Extract occasion/place to wear from AI description"""
        description_lower = description.lower()
        
        # Direct occasion matches
        for occasion, keywords in self.occasion_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return occasion
        
        # Contextual occasion detection
        if any(word in description_lower for word in ['suit', 'formal', 'tuxedo', 'gown', 'elegant']):
            return 'formal'
        elif any(word in description_lower for word in ['workout', 'athletic', 'sports', 'gym', 'exercise']):
            return 'athletic'
        elif any(word in description_lower for word in ['office', 'work', 'business', 'professional']):
            return 'business'
        elif any(word in description_lower for word in ['beach', 'pool', 'swim']):
            return 'beachwear'
        elif any(word in description_lower for word in ['party', 'celebration', 'club']):
            return 'party'
        elif any(word in description_lower for word in ['casual', 'everyday', 't-shirt', 'jeans']):
            return 'casual'
        
        # Default to 'casual' instead of returning None
        return 'casual'
    
    def _enhanced_rule_analysis(self, image: Image.Image) -> Dict[str, Any]:
        """Enhanced rule-based analysis"""
        try:
            logger.info("Running enhanced rule-based analysis...")
            
            # Get image dimensions
            width, height = image.size
            aspect_ratio = width / height
            
            # Analyze dominant colors
            dominant_color = self._analyze_dominant_color(image)
            
            # Classify category using multiple factors
            category, confidence = self._classify_category_enhanced(aspect_ratio, dominant_color)
            
            # Suggest occasion based on category and color
            occasion = self._suggest_occasion(category, dominant_color)
            
            result = {
                'suggestedCategory': category,
                'suggestedColor': dominant_color,
                'confidence': confidence,
                'analysis_method': 'enhanced_rule_based',
                'features': {
                    'aspect_ratio': aspect_ratio,
                    'dominant_color': dominant_color
                },
                'detected_colors': [dominant_color],
                'success': True
            }
            
            # Add occasion if detected
            if occasion:
                result['suggestedOccasion'] = occasion
                result['features']['occasion'] = occasion
                
            return result
            
        except Exception as e:
            logger.error(f"Rule-based analysis failed: {e}")
            return self._create_fallback_response()
    
    def _analyze_dominant_color(self, image: Image.Image) -> str:
        """Analyze dominant color"""
        try:
            # Resize for faster processing
            small_image = image.resize((50, 50))
            pixels = np.array(small_image).reshape(-1, 3)
            
            # Calculate average RGB
            r_avg = int(np.mean(pixels[:, 0]))
            g_avg = int(np.mean(pixels[:, 1]))
            b_avg = int(np.mean(pixels[:, 2]))
            
            # Convert to color name
            return self._rgb_to_color_name(r_avg, g_avg, b_avg)
            
        except Exception as e:
            logger.error(f"Color analysis failed: {e}")
            return 'Unknown'
    
    def _classify_category_enhanced(self, aspect_ratio: float, color: str) -> Tuple[str, float]:
        """Enhanced category classification"""
        try:
            # Category logic
            if aspect_ratio > 2.5:
                return 'shoes', 0.8
            elif aspect_ratio < 0.5:
                return 'dresses', 0.7
            elif color in ['Pink', 'Red', 'Purple'] and aspect_ratio < 1.2:
                return 'dresses', 0.6
            elif 0.8 <= aspect_ratio <= 1.3:
                return 'tops', 0.6
            else:
                return 'bottoms', 0.5
                
        except Exception:
            return 'tops', 0.4
    
    def _rgb_to_color_name(self, r: int, g: int, b: int) -> str:
        """Convert RGB values to color name"""
        try:
            # Handle extreme cases
            if r > 240 and g > 240 and b > 240:
                return 'White'
            if r < 40 and g < 40 and b < 40:
                return 'Black'
            
            # Color detection logic
            if r > 180 and g < 100 and b < 100:
                return 'Red'
            elif r < 100 and g < 100 and b > 180:
                return 'Blue'
            elif r < 100 and g > 180 and b < 100:
                return 'Green'
            elif r > 180 and g > 180 and b < 100:
                return 'Yellow'
            elif r > 150 and g < 120 and b > 150:
                return 'Pink'
            elif r > 120 and g < 100 and b > 120:
                return 'Purple'
            elif r > 180 and g > 100 and b < 80:
                return 'Orange'
            elif r > 100 and g > 80 and b < 80:
                return 'Brown'
            else:
                return 'Gray'
                
        except Exception:
            return 'Unknown'
    
    def _create_fallback_response(self) -> Dict[str, Any]:
        """Create a basic fallback response"""
        return {
            'suggestedCategory': 'tops',
            'suggestedColor': 'Unknown',
            'suggestedOccasion': 'casual',
            'confidence': 0.4,
            'analysis_method': 'basic_fallback',
            'detected_colors': ['Unknown'],
            'success': True
        }
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create an error response"""
        return {
            'suggestedCategory': 'tops',
            'suggestedColor': 'Unknown',
            'suggestedOccasion': 'casual',
            'confidence': 0.3,
            'analysis_method': 'error_fallback',
            'detected_colors': ['Unknown'],
            'error': error_message,
            'success': False
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            'ai_models_loaded': self.ai_loaded,
            'supported_categories': list(self.category_keywords.keys()),
            'supported_colors': list(self.color_keywords.keys()),
            'supported_occasions': list(self.occasion_keywords.keys()) if hasattr(self, 'occasion_keywords') else [],
            'analysis_methods': [
                'free_huggingface_ai' if self.ai_loaded else None,
                'enhanced_rule_based',
                'basic_fallback'
            ],
            'features': {
                'color_detection': True,
                'category_detection': True,
                'occasion_detection': hasattr(self, 'occasion_keywords'),
                'confidence_scoring': True,
                'fallback_capabilities': True
            }
        }

    def _suggest_occasion(self, category: str, color: str) -> str:
        """Suggest occasion based on category and color"""
        # Map categories to likely occasions
        category_to_occasion = {
            'formal': 'formal',
            'sportswear': 'athletic',
            'tops': 'casual',
            'bottoms': 'casual',
            'dresses': 'formal',
            'outerwear': 'casual',
            'accessories': None,
            'shoes': None,
            'sleepwear': None,
            'underwear': None
        }
        
        # Color can influence occasion
        color_to_occasion = {
            'Black': 'formal',
            'White': None,
            'Red': None,
            'Blue': None,
            'Gray': 'business',
            'Brown': 'business',
            'Metallic': 'formal'
        }
        
        # Try category-based occasion first
        if category in category_to_occasion and category_to_occasion[category]:
            return category_to_occasion[category]
            
        # Then try color-based occasion
        if color in color_to_occasion and color_to_occasion[color]:
            return color_to_occasion[color]
            
        # Default to casual for most items
        return 'casual'

# Global instance
free_ai_analyzer = FreeAIClothingAnalyzer()