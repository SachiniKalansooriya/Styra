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
        
        # Places to wear / occasions with enhanced detection
        self.occasion_keywords = {
            'casual': ['everyday', 'casual', 'daily', 'relaxed', 'lounging', 'weekend', 'around town', 
                     'errands', 'informal', 'laid-back', 'street style', 'comfortable', 'easy-going'],
            'formal': ['formal', 'elegant', 'fancy', 'sophisticated', 'dressy', 'black tie', 'gala', 
                     'ceremony', 'wedding', 'cocktail', 'upscale', 'evening', 'classy', 'refined'],
            'business': ['office', 'work', 'professional', 'business', 'corporate', 'meeting', 'presentation', 
                       'interview', 'workplace', 'business casual', 'boardroom', 'executive'],
            'work': ['office', 'work', 'professional', 'business', 'corporate', 'meeting', 'presentation', 
                       'interview', 'workplace', 'business casual', 'boardroom', 'executive'],
            'athletic': ['gym', 'workout', 'exercise', 'sports', 'fitness', 'running', 'training', 'yoga', 
                       'athletic', 'jogging', 'hiking', 'outdoor activities', 'cardio', 'strength'],
            'workout': ['gym', 'workout', 'exercise', 'sports', 'fitness', 'running', 'training', 'yoga', 
                       'athletic', 'jogging', 'hiking', 'outdoor activities', 'cardio', 'strength'],
            'beachwear': ['beach', 'pool', 'swim', 'swimming', 'resort', 'vacation', 'tropical', 'cruise', 
                        'sunbathing', 'waterside'],
            'party': ['party', 'club', 'nightout', 'celebration', 'festive', 'dance', 'nightclub', 
                    'birthday', 'entertainment', 'social event'],
            'datenight': ['date', 'romantic', 'dinner', 'night out', 'restaurant', 'special occasion',
                        'intimate', 'charming', 'attractive', 'stylish'],
            'date': ['date', 'romantic', 'dinner', 'night out', 'restaurant', 'special occasion',
                        'intimate', 'charming', 'attractive', 'stylish'],
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
        """Extract clothing category from AI description with improved accuracy"""
        description_lower = description.lower()
        
        # Check for direct category keywords in description (prioritize exact matches)
        exact_matches = []
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    # Give higher weight to longer, more specific keywords
                    weight = len(keyword) / 10.0  # Longer keywords get higher weight
                    exact_matches.append((category, keyword, weight))
        
        # If we have exact matches, prioritize them
        if exact_matches:
            # Sort by weight (longer, more specific keywords first)
            exact_matches.sort(key=lambda x: x[2], reverse=True)
            best_match = exact_matches[0]
            confidence = 0.85 + min(best_match[2] * 0.1, 0.1)  # Bonus for specific keywords
            return best_match[0], confidence
        
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
            
            # Add context-based scores with improved logic
            if category == 'tops' and any(w in description_lower for w in ['shirt', 'wearing', 'top', 'blouse', 'sweater']):
                score += 0.3
            elif category == 'bottoms' and any(w in description_lower for w in ['pants', 'trousers', 'jeans', 'shorts', 'wearing pants', 'office pants']):
                score += 0.3
            elif category == 'dresses' and any(w in description_lower for w in ['woman', 'wearing', 'dress', 'gown']):
                score += 0.3
            elif category == 'formal' and any(w in description_lower for w in ['formal', 'suit', 'elegant', 'business', 'office']):
                score += 0.25
            elif category == 'sportswear' and any(w in description_lower for w in ['sport', 'athletic', 'workout', 'gym']):
                score += 0.25
            elif category == 'shoes' and any(w in description_lower for w in ['shoes', 'boots', 'sneakers', 'footwear']):
                score += 0.3
            elif category == 'outerwear' and any(w in description_lower for w in ['jacket', 'coat', 'blazer', 'cardigan']):
                score += 0.3
                
            # Special handling for office/business clothing
            if 'office' in description_lower or 'business' in description_lower or 'professional' in description_lower:
                if category == 'bottoms' and any(w in description_lower for w in ['pants', 'trousers']):
                    score += 0.4
                elif category == 'formal':
                    score += 0.3
                    
            category_scores[category] = score
        
        # Get best scoring category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:
                confidence = min(0.5 + best_category[1], 0.9)
                return best_category[0], confidence
        
        # Default based on common words with better logic
        if any(word in description_lower for word in ['pants', 'trousers', 'jeans', 'shorts']):
            return 'bottoms', 0.7
        elif any(word in description_lower for word in ['wearing', 'person', 'man', 'woman']):
            return 'tops', 0.6
        
        return 'tops', 0.4
    
    def _extract_color_from_description(self, description: str) -> str:
        """Extract color from AI description with improved accuracy"""
        description_lower = description.lower()
        
        # Check for direct color keywords in description (prioritize exact matches)
        exact_matches = []
        for color, keywords in self.color_keywords.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    exact_matches.append((color, keyword))
        
        # If we have exact matches, prioritize more specific color names
        if exact_matches:
            # Sort by keyword length (longer keywords are usually more specific)
            exact_matches.sort(key=lambda x: len(x[1]), reverse=True)
            return exact_matches[0][0]
        
        # Check for compound colors with modifiers
        color_modifiers = ['dark', 'light', 'pale', 'bright', 'deep', 'vivid', 'muted', 'soft']
        for modifier in color_modifiers:
            pattern = f'{modifier}\\s+(\\w+)'
            color_words = re.findall(pattern, description_lower)
            for color_word in color_words:
                for color, keywords in self.color_keywords.items():
                    if color_word in [k.lower() for k in keywords]:
                        return color
        
        # Check for color patterns and textures that might indicate specific colors
        pattern_indicators = {
            'Green': ['olive', 'forest', 'military', 'khaki', 'sage', 'mint'],
            'Blue': ['navy', 'denim', 'royal', 'sky', 'turquoise', 'teal'],
            'Brown': ['tan', 'beige', 'camel', 'chocolate', 'coffee', 'leather'],
            'Gray': ['charcoal', 'slate', 'ash', 'stone'],
            'Red': ['burgundy', 'wine', 'crimson', 'cherry'],
            'Black': ['charcoal', 'midnight', 'ebony'],
            'White': ['ivory', 'cream', 'pearl', 'off-white']
        }
        
        for color, indicators in pattern_indicators.items():
            if any(indicator in description_lower for indicator in indicators):
                return color
        
        # Check for generic color descriptions
        if any(word in description_lower for word in ['colorful', 'multi-colored', 'multicolor', 'patterned', 'floral', 'striped']):
            return 'Multicolor'
        elif any(word in description_lower for word in ['dark colored', 'dark tone', 'shadowy']):
            return 'Black'
        elif any(word in description_lower for word in ['light colored', 'bright', 'pale']):
            return 'White'
        
        return 'Unknown'
    
    def _extract_occasion_from_description(self, description: str) -> str:
        """Extract occasion/place to wear from AI description with enhanced accuracy"""
        description_lower = description.lower()
        
        # Weighted occasion scoring for better accuracy
        occasion_scores = {}
        
        # Direct keyword matching with weights
        for occasion, keywords in self.occasion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    # Longer, more specific keywords get higher weight
                    weight = len(keyword.split()) * 2 + len(keyword) / 10
                    score += weight
            occasion_scores[occasion] = score
        
        # Category and style-based occasion detection
        if any(word in description_lower for word in ['suit', 'formal', 'tuxedo', 'gown', 'elegant', 'dress shirt']):
            occasion_scores['formal'] = occasion_scores.get('formal', 0) + 10
        elif any(word in description_lower for word in ['workout', 'athletic', 'sports', 'gym', 'exercise', 'running', 'yoga']):
            occasion_scores['workout'] = occasion_scores.get('workout', 0) + 10
        elif any(word in description_lower for word in ['office', 'work', 'business', 'professional', 'blazer', 'button']):
            occasion_scores['work'] = occasion_scores.get('work', 0) + 8
        elif any(word in description_lower for word in ['party', 'club', 'night', 'dressy', 'going out']):
            if any(word in description_lower for word in ['date', 'romantic', 'dinner']):
                occasion_scores['datenight'] = occasion_scores.get('datenight', 0) + 8
            else:
                occasion_scores['party'] = occasion_scores.get('party', 0) + 6
        elif any(word in description_lower for word in ['casual', 'everyday', 't-shirt', 'jeans', 'comfortable']):
            occasion_scores['casual'] = occasion_scores.get('casual', 0) + 6
        
        # Specific datenight items boost
        if any(word in description_lower for word in ['dress', 'frock', 'denim', 'cute', 'nice top', 'crop top']):
            occasion_scores['datenight'] = occasion_scores.get('datenight', 0) + 5
        
        # Color and style hints for occasions
        if any(word in description_lower for word in ['red', 'black dress', 'elegant', 'stylish']):
            occasion_scores['datenight'] = occasion_scores.get('datenight', 0) + 3
        elif any(word in description_lower for word in ['navy', 'gray', 'professional']):
            occasion_scores['work'] = occasion_scores.get('work', 0) + 3
        elif any(word in description_lower for word in ['colorful', 'bright', 'fun']):
            occasion_scores['casual'] = occasion_scores.get('casual', 0) + 2
        
        # Find the highest scoring occasion
        if occasion_scores:
            best_occasion = max(occasion_scores.items(), key=lambda x: x[1])
            if best_occasion[1] > 0:
                return best_occasion[0]
        
        # Enhanced default logic based on clothing type
        if any(word in description_lower for word in ['dress', 'skirt', 'blouse', 'nice']):
            return 'datenight'
        elif any(word in description_lower for word in ['pants', 'shirt', 'top']):
            return 'work'
        
        # Default to 'casual' 
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
        """Analyze dominant color with improved accuracy"""
        try:
            # Resize for faster processing but keep reasonable size for accuracy
            small_image = image.resize((100, 100))
            pixels = np.array(small_image).reshape(-1, 3)
            
            # Remove very dark and very light pixels (likely shadows/highlights)
            # This helps focus on the actual clothing color
            filtered_pixels = []
            for pixel in pixels:
                r, g, b = pixel
                brightness = (r + g + b) / 3
                if 30 < brightness < 225:  # Skip very dark and very bright pixels
                    filtered_pixels.append(pixel)
            
            if not filtered_pixels:
                # If no pixels pass the filter, use all pixels
                filtered_pixels = pixels
            
            filtered_pixels = np.array(filtered_pixels)
            
            # Calculate average RGB from filtered pixels
            r_avg = int(np.mean(filtered_pixels[:, 0]))
            g_avg = int(np.mean(filtered_pixels[:, 1]))
            b_avg = int(np.mean(filtered_pixels[:, 2]))
            
            # Also calculate the most frequent color (mode)
            unique_colors, counts = np.unique(filtered_pixels, axis=0, return_counts=True)
            most_frequent_color = unique_colors[np.argmax(counts)]
            
            # Use both average and most frequent for more accurate detection
            avg_color = self._rgb_to_color_name(r_avg, g_avg, b_avg)
            freq_color = self._rgb_to_color_name(most_frequent_color[0], most_frequent_color[1], most_frequent_color[2])
            
            # If both methods agree, use that color
            if avg_color == freq_color:
                return avg_color
            
            # If they disagree, use the one with higher confidence
            avg_confidence = self._get_color_confidence(r_avg, g_avg, b_avg)
            freq_confidence = self._get_color_confidence(most_frequent_color[0], most_frequent_color[1], most_frequent_color[2])
            
            if avg_confidence > freq_confidence:
                return avg_color
            else:
                return freq_color
            
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
        """Convert RGB values to color name with improved accuracy"""
        try:
            # Handle extreme cases first
            if r > 240 and g > 240 and b > 240:
                return 'White'
            if r < 40 and g < 40 and b < 40:
                return 'Black'
            
            # Calculate color distances to predefined color centers
            color_centers = {
                'Red': (220, 20, 60),      # Crimson
                'Green': (34, 139, 34),    # Forest Green
                'Blue': (30, 144, 255),    # Dodger Blue
                'Yellow': (255, 215, 0),   # Gold
                'Orange': (255, 140, 0),   # Dark Orange
                'Purple': (128, 0, 128),   # Purple
                'Pink': (255, 20, 147),    # Deep Pink
                'Brown': (139, 69, 19),    # Saddle Brown
                'Gray': (128, 128, 128),   # Gray
                'White': (255, 255, 255),  # White
                'Black': (0, 0, 0),        # Black
            }
            
            # Calculate Euclidean distance to each color center
            min_distance = float('inf')
            closest_color = 'Gray'
            
            for color_name, (cr, cg, cb) in color_centers.items():
                distance = np.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_color = color_name
            
            # Additional logic for better color distinction
            # Check if it's clearly one color channel dominant
            max_channel = max(r, g, b)
            min_channel = min(r, g, b)
            
            # If there's high contrast between channels
            if max_channel - min_channel > 80:
                if r == max_channel and r > g + 50 and r > b + 50:
                    # Strong red component
                    if g > 100:  # Red with significant green might be orange
                        return 'Orange'
                    return 'Red'
                elif g == max_channel and g > r + 50 and g > b + 50:
                    # Strong green component
                    return 'Green'
                elif b == max_channel and b > r + 50 and b > g + 50:
                    # Strong blue component
                    return 'Blue'
            
            # Check for specific color combinations
            if r > 150 and g > 150 and b < 100:
                return 'Yellow'
            elif r > 150 and g < 100 and b > 150:
                return 'Purple'
            elif r > 200 and g > 100 and b > 150:
                return 'Pink'
            elif r > 100 and g > 80 and b < 80 and r > g:
                return 'Brown'
            elif abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30:
                # Colors are similar - it's grayscale
                if r > 180:
                    return 'White'
                elif r < 80:
                    return 'Black'
                else:
                    return 'Gray'
            
            return closest_color
                
        except Exception as e:
            logger.error(f"RGB to color conversion failed: {e}")
            return 'Unknown'
    
    def _get_color_confidence(self, r: int, g: int, b: int) -> float:
        """Calculate confidence score for color detection"""
        try:
            # Check color saturation (how "pure" the color is)
            max_channel = max(r, g, b)
            min_channel = min(r, g, b)
            saturation = (max_channel - min_channel) / max_channel if max_channel > 0 else 0
            
            # Check brightness
            brightness = (r + g + b) / 3
            brightness_score = 1.0 - abs(brightness - 127.5) / 127.5  # Prefer mid-brightness
            
            # Combine saturation and brightness for confidence
            confidence = (saturation * 0.7) + (brightness_score * 0.3)
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5
    
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
            'dresses': 'datenight',  # Changed from 'formal' to be more flexible for datenight
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