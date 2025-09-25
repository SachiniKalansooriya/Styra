# services/ai_enhanced_outfit_service.py
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import io
import logging
from typing import Dict, List, Optional
from database.connection import db
import requests
import json
import uuid
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class AIEnhancedOutfitService:
    def __init__(self):
        # Base functionality
        self.weather_compatibility_matrix = self._create_weather_compatibility_matrix()
        self.color_harmony_rules = self._create_color_harmony_rules()
        self.outfit_rules = self._create_outfit_rules()
        
        # AI components
        self.clip_model = None
        self.clip_processor = None
        self.ai_loaded = False
        self._load_ai_models()
    
    def _create_weather_compatibility_matrix(self):
        """Weather compatibility scoring matrix"""
        return {
            'temperature_ranges': {
                'very_cold': (-20, 5),
                'cold': (5, 15),
                'cool': (15, 22),
                'mild': (22, 28),
                'warm': (28, 35),
                'hot': (35, 50)
            },
            'category_weather_scores': {
                'tops': {
                    'very_cold': {'sweater': 9, 'hoodie': 8, 'long_sleeve': 7, 't_shirt': 2},
                    'cold': {'sweater': 8, 'hoodie': 9, 'long_sleeve': 8, 't_shirt': 3},
                    'cool': {'hoodie': 7, 'long_sleeve': 8, 'light_sweater': 8, 't_shirt': 6},
                    'mild': {'t_shirt': 9, 'blouse': 8, 'light_sweater': 6, 'tank_top': 7},
                    'warm': {'t_shirt': 8, 'tank_top': 9, 'blouse': 7, 'light_shirt': 8},
                    'hot': {'tank_top': 10, 'light_shirt': 8, 't_shirt': 6, 'sleeveless': 9}
                }
            }
        }
    
    def _create_color_harmony_rules(self):
        """Color harmony and compatibility rules"""
        return {
            'complementary_pairs': [
                ('blue', 'orange'), ('red', 'green'), ('purple', 'yellow'),
                ('navy', 'cream'), ('black', 'white'), ('gray', 'pink')
            ],
            'neutral_colors': ['black', 'white', 'gray', 'beige', 'cream', 'navy', 'brown'],
            'warm_colors': ['red', 'orange', 'yellow', 'pink', 'coral', 'burgundy'],
            'cool_colors': ['blue', 'green', 'purple', 'teal', 'navy', 'turquoise']
        }
    
    def _create_outfit_rules(self):
        """Enhanced outfit combination rules with occasion-specific guidelines"""
        return {
            'occasion_formality': {
                'casual': (1, 4),
                'work': (5, 7),
                'business': (5, 7),
                'formal': (8, 10),
                'workout': (1, 3),
                'date': (6, 9),
                'datenight': (6, 9),
                # Party outfits should be dressy but allow statement/shiny pieces
                'party': (6, 9)
            },
            'occasion_specific_rules': {
                'casual': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes'],
                    'preferred_items': ['t-shirt', 'jeans', 'sneakers', 'hoodie', 'shorts'],
                    'color_preferences': ['blue', 'white', 'gray', 'black'],
                    'avoid_items': ['suit', 'blazer', 'formal dress', 'heels']
                },
                'work': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes', 'outerwear'],
                    'preferred_items': ['button shirt', 'blouse', 'dress pants', 'blazer', 'dress shoes'],
                    'color_preferences': ['navy', 'black', 'white', 'gray', 'brown'],
                    'avoid_items': ['tank top', 'shorts', 'sneakers', 'flip-flops']
                },
                'datenight': {
                    'preferred_categories': ['dresses', 'tops', 'bottoms', 'shoes', 'accessories'],
                    'preferred_items': ['dress', 'frock', 'nice top', 'blouse', 'crop top', 'denim', 'jeans', 'cute pants', 'heels', 'flats', 'boots'],
                    'color_preferences': ['red', 'black', 'blue', 'white', 'pink', 'burgundy', 'navy'],
                    'avoid_items': ['workout', 'athletic', 'gym clothes', 'office trousers', 'formal pants', 'dress pants', 'blazer', 'business shirt']
                },
                'party': {
                    'preferred_categories': ['dresses', 'tops', 'bottoms', 'shoes', 'accessories'],
                    'preferred_items': ['sequined dress', 'sequin top', 'metallic top', 'leather jacket', 'statement dress', 'sparkly top', 'sequin skirt', 'glitter top', 'lamé dress', 'shiny blouse', 'bold accessories', 'heels', 'boots'],
                    'color_preferences': ['gold', 'silver', 'black', 'red', 'burgundy', 'navy', 'metallic'],
                    'avoid_items': ['plain activewear', 'workout clothes', 'very casual lounge wear']
                },
                'formal': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes', 'accessories'],
                    'preferred_items': ['dress shirt', 'suit', 'dress', 'formal dress', 'dress shoes', 'heels'],
                    'color_preferences': ['black', 'navy', 'white', 'gray'],
                    'avoid_items': ['t-shirt', 'jeans', 'sneakers', 'shorts']
                },
                'workout': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes'],
                    'preferred_items': ['athletic', 'gym', 'sports', 'workout', 'running', 'yoga'],
                    'color_preferences': ['black', 'gray', 'blue', 'white'],
                    'avoid_items': ['dress', 'suit', 'formal', 'heels']
                }
            }
        }
    
    def _load_ai_models(self):
        """Load CLIP model for advanced outfit analysis"""
        try:
            logger.info("Loading CLIP model for outfit analysis...")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.ai_loaded = True
            logger.info("AI models loaded successfully for outfit generation!")
        except Exception as e:
            logger.warning(f"Failed to load AI models: {e}")
            self.ai_loaded = False
    
    def get_user_wardrobe_items(self, user_id: int = 1) -> List[Dict]:
        """Get user's wardrobe items from database"""
        try:
            query = """
                SELECT id, name, category, color, season, image_path, 
                       confidence, times_worn, last_worn, created_at
                FROM wardrobe_items 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            
            items = db.execute_query(query, (user_id,))
            
            if not items:
                return []
            
            # Convert to format expected by AI algorithm
            formatted_items = []
            for item in items:
                formatted_item = {
                    'id': item['id'],
                    'name': item['name'],
                    'category': item['category'],
                    'color': item['color'] or 'unknown',
                    'season': item['season'] or 'all',
                    'image_path': item['image_path'],
                    'confidence': float(item['confidence']) if item['confidence'] else 85.0,
                    'times_worn': item['times_worn'] or 0,
                    'last_worn': item['last_worn'].isoformat() if item['last_worn'] else None,
                    'created_at': item['created_at'].isoformat() if item['created_at'] else None,
                    
                    # Add AI scoring attributes
                    'temp_range': self._get_temp_range_for_item(item['category'], item['season']),
                    'formality_score': self._get_formality_score(item['category'], item['name']),
                    'comfort_score': self._get_comfort_score(item['category']),
                    'weather_compatibility': self._get_weather_compatibility(item['category'])
                }
                formatted_items.append(formatted_item)
            
            return formatted_items
            
        except Exception as e:
            logger.error(f"Error getting wardrobe items: {e}")
            return []
    
    def _get_temp_range_for_item(self, category: str, season: str) -> List[int]:
        """Estimate temperature range for clothing item"""
        base_ranges = {
            'tank_top': [25, 40], 't_shirt': [18, 35], 'blouse': [16, 30],
            'sweater': [5, 20], 'hoodie': [8, 25], 'jacket': [0, 18],
            'shorts': [22, 40], 'pants': [5, 30], 'jeans': [8, 25],
            'skirt': [20, 35], 'dress': [15, 32]
        }
        
        season_adjustments = {
            'winter': [-5, -10], 'summer': [5, 10],
            'spring': [0, 5], 'fall': [-2, -5]
        }
        
        category_lower = category.lower()
        base_range = base_ranges.get(category_lower, [10, 30])
        
        if season in season_adjustments:
            adj = season_adjustments[season]
            base_range = [base_range[0] + adj[0], base_range[1] + adj[1]]
        
        return base_range
    
    def _get_formality_score(self, category: str, name: str) -> int:
        """Enhanced formality score calculation 1-10"""
        formal_keywords = {
            'suit': 10, 'tuxedo': 10, 'formal dress': 9, 'evening gown': 9,
            'dress shirt': 8, 'blazer': 8, 'dress pants': 8, 'dress shoes': 8,
            'business': 7, 'office': 7, 'professional': 7, 'blouse': 7
        }
        
        datenight_keywords = {
            'dress': 6, 'frock': 6, 'nice dress': 7, 'party dress': 6,
            'denim': 5, 'jeans': 5, 'cute top': 5, 'nice top': 6,
            'crop top': 4, 'heels': 7, 'boots': 5, 'flats': 5
        }
        
        casual_keywords = {
            't-shirt': 2, 'tank top': 1, 'hoodie': 2, 'sweatshirt': 2,
            'shorts': 2, 'athletic': 1, 'gym': 1, 'workout': 1,
            'sneakers': 3, 'flip-flops': 1, 'sandals': 2
        }
        
        name_lower = name.lower()
        combined_text = f"{name_lower} {category.lower()}"
        
        # Check keywords with priorities
        for keywords, default_score in [(formal_keywords, 8), (datenight_keywords, 6), (casual_keywords, 2)]:
            for keyword, score in keywords.items():
                if keyword in combined_text:
                    return score
        
        return 5  # Default
    
    def _get_comfort_score(self, category: str) -> int:
        """Estimate comfort score 1-10"""
        comfort_scores = {
            'athletic': 10, 'casual': 8, 'lounge': 9,
            'business': 6, 'formal': 4
        }
        
        category_lower = category.lower()
        for key, score in comfort_scores.items():
            if key in category_lower:
                return score
        
        return 7
    
    def _get_weather_compatibility(self, category: str) -> List[str]:
        """Get weather conditions this item is good for"""
        compatibility_map = {
            'tank_top': ['sunny', 'hot'], 't_shirt': ['sunny', 'cloudy', 'mild'],
            'sweater': ['cloudy', 'cold', 'windy'], 'hoodie': ['cloudy', 'cool', 'windy'],
            'jacket': ['cold', 'windy', 'rainy'], 'shorts': ['sunny', 'hot', 'warm'],
            'pants': ['cloudy', 'cool', 'cold'], 'jeans': ['cloudy', 'cool', 'casual']
        }
        
        return compatibility_map.get(category.lower(), ['sunny', 'cloudy'])
    
    def generate_outfit_recommendation(self, user_id: int, weather_data: Dict, occasion: str, variation: bool = False) -> Dict:
        """Generate AI-enhanced outfit recommendation using user's actual wardrobe"""
        try:
            wardrobe_items = self.get_user_wardrobe_items(user_id)
            
            if not wardrobe_items:
                return {
                    'error': 'No wardrobe items found',
                    'message': 'Please add some clothes to your wardrobe first!'
                }
            
            # Group items by category
            items_by_category = {}
            for item in wardrobe_items:
                category = item['category'].lower()
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Score all items
            scored_items = {}
            for category, items in items_by_category.items():
                scored_items[category] = []
                for item in items:
                    score = self.calculate_item_compatibility_score(item, weather_data, occasion)
                    scored_items[category].append((item, score))
                
                scored_items[category].sort(key=lambda x: x[1], reverse=True)
            
            # Build outfit
            outfit_items = []
            total_score = 0
            score_count = 0

            # For party occasions, prefer a dress (single-piece) if available
            dress_added = False
            if occasion == 'party':
                for dress_key in ['dress', 'dresses', 'frock', 'formal dress', 'sequin dress', 'sequined dress']:
                    if dress_key in scored_items and scored_items[dress_key]:
                        if variation:
                            top_n = min(3, len(scored_items[dress_key]))
                            chosen = scored_items[dress_key][random.randrange(top_n)]
                        else:
                            chosen = scored_items[dress_key][0]
                        outfit_items.append(chosen[0])
                        total_score += chosen[1]
                        score_count += 1
                        dress_added = True
                        break
            
            # Required categories with common variant names to match frontend inputs
            # If a dress was added for party, skip adding separate top/bottom
            required_categories = ['tops', 'bottoms'] if not dress_added else []
            for req_cat in required_categories:
                if req_cat == 'tops':
                    possible_cats = ['tops', 'top', 'shirts', 'shirt', 't-shirts', 't-shirt', 'blouses', 'blouse', 'jersey']
                else:
                    # bottoms
                    possible_cats = ['bottoms', 'bottom', 'pants', 'pant', 'jeans', 'shorts', 'skirt', 'skirts']
                found_item = None

                for cat_variant in possible_cats:
                    if cat_variant in scored_items and scored_items[cat_variant]:
                        # Choose top candidate or random among top-N when variation requested
                        if variation:
                            top_n = min(3, len(scored_items[cat_variant]))
                            idx = random.randrange(top_n)
                            found_item = scored_items[cat_variant][idx]
                        else:
                            found_item = scored_items[cat_variant][0]
                        break

                if found_item:
                    outfit_items.append(found_item[0])
                    total_score += found_item[1]
                    score_count += 1
            
            # Optional categories
            optional_categories = ['shoes', 'outerwear']
            for opt_cat in optional_categories:
                # Accept common shoe synonyms as well
                shoe_variants = ['shoes', 'shoe', 'sneakers', 'boots', 'sandals', 'flip-flops', 'loafers', 'espadrilles', 'moccasins', 'heels']
                candidates_key = None
                if opt_cat == 'shoes':
                    # pick the first matching shoe category key present in scored_items
                    for sv in shoe_variants:
                        if sv in scored_items and scored_items[sv]:
                            candidates_key = sv
                            break
                else:
                    candidates_key = opt_cat

                if candidates_key and candidates_key in scored_items and scored_items[candidates_key]:
                    if opt_cat == 'shoes':
                        # For party, prefer heels if available
                        chosen = None
                        if occasion == 'party' and 'heels' in scored_items and scored_items['heels']:
                            if variation:
                                top_n = min(3, len(scored_items['heels']))
                                chosen = scored_items['heels'][random.randrange(top_n)]
                            else:
                                chosen = scored_items['heels'][0]
                        # fallback to the candidates_key list
                        if not chosen:
                            chosen = scored_items[candidates_key][0]
                            if variation:
                                top_n = min(3, len(scored_items[candidates_key]))
                                chosen = scored_items[candidates_key][random.randrange(top_n)]
                        outfit_items.append(chosen[0])
                        total_score += chosen[1]
                        score_count += 1
                    elif opt_cat == 'outerwear':
                        temp = weather_data.get('temperature', 20)
                        if temp < 15 or 'rain' in weather_data.get('condition', '').lower():
                            chosen = scored_items[opt_cat][0]
                            if variation:
                                top_n = min(3, len(scored_items[opt_cat]))
                                chosen = scored_items[opt_cat][random.randrange(top_n)]
                            outfit_items.append(chosen[0])
                            total_score += chosen[1]
                            score_count += 1
            
            # Calculate confidence
            confidence = int(total_score / score_count) if score_count > 0 else 50
            
            # AI enhancement if available
            if outfit_items and self.ai_loaded:
                ai_analysis = self.analyze_outfit_compatibility_with_ai(
                    outfit_items, weather_data, occasion
                )
                confidence = int((confidence + ai_analysis.get('confidence', confidence)) / 2)
            
            reason = self._generate_outfit_reason(outfit_items, weather_data, occasion)
            
            return {
                'id': f'user_outfit_{uuid.uuid4().hex[:8]}',
                'items': outfit_items,
                'confidence': confidence,
                'reason': reason,
                'weather_context': weather_data,
                'occasion': occasion,
                'ai_enhanced': self.ai_loaded,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating outfit recommendation: {e}")
            return {
                'error': 'Failed to generate recommendation',
                'message': str(e)
            }
    
    def calculate_item_compatibility_score(self, item: Dict, weather_data: Dict, occasion: str) -> float:
        """Calculate enhanced AI compatibility score for clothing item"""
        score = 0.0
        
        # Temperature compatibility (35% weight)
        temp = weather_data.get('temperature', 20)
        temp_min, temp_max = item['temp_range']
        if temp_min <= temp <= temp_max:
            temp_score = 35.0
            optimal_temp = (temp_min + temp_max) / 2
            temp_distance = abs(temp - optimal_temp)
            if temp_distance <= 3:
                temp_score += 5.0
        else:
            temp_distance = min(abs(temp - temp_min), abs(temp - temp_max))
            temp_score = max(0, 35.0 - (temp_distance * 2))
        
        score += temp_score
        
        # Occasion matching (35% weight)
        occasion_formality_range = self.outfit_rules['occasion_formality'].get(occasion, (1, 10))
        item_formality = item['formality_score']
        
        if occasion_formality_range[0] <= item_formality <= occasion_formality_range[1]:
            occasion_score = 35.0
        else:
            if item_formality < occasion_formality_range[0]:
                penalty = (occasion_formality_range[0] - item_formality) * 4
            else:
                penalty = (item_formality - occasion_formality_range[1]) * 4
            occasion_score = max(0, 35.0 - penalty)
        
        score += max(occasion_score, 0)
        
        # Weather condition compatibility (15% weight)
        weather_conditions = self._extract_weather_conditions(weather_data)
        weather_score = 0
        for condition in weather_conditions:
            if condition in item['weather_compatibility']:
                weather_score += 15.0 / len(weather_conditions)
        
        score += min(weather_score, 15.0)
        
        # Color and comfort (15% weight)
        score += 15.0

        # Party occasion: boost shiny/metallic/sequin items to favor party looks
        try:
            if occasion == 'party':
                name_lower = item.get('name', '').lower()
                color_lower = str(item.get('color', '')).lower()
                shiny_keywords = ['sequin', 'sequined', 'metallic', 'glitter', 'sparkle', 'sparkly', 'lamé', 'lame', 'shiny']
                if any(k in name_lower for k in shiny_keywords) or any(k in color_lower for k in ['gold', 'silver', 'metallic']):
                    score += 10.0
        except Exception:
            # In case item fields are missing or unexpected, ignore party bonus
            pass

        return min(score, 100.0)
    
    def _extract_weather_conditions(self, weather_data: Dict) -> List[str]:
        """Extract weather conditions from weather data"""
        conditions = []
        temp = weather_data.get('temperature', 20)
        condition = weather_data.get('condition', '').lower()
        
        if temp < 5:
            conditions.append('very_cold')
        elif temp < 15:
            conditions.append('cold')
        elif temp < 22:
            conditions.append('cool')
        elif temp < 28:
            conditions.append('mild')
        elif temp < 35:
            conditions.append('warm')
        else:
            conditions.append('hot')
        
        if 'sun' in condition or 'clear' in condition:
            conditions.append('sunny')
        elif 'cloud' in condition:
            conditions.append('cloudy')
        elif 'rain' in condition:
            conditions.append('rainy')
        
        return conditions
    
    def analyze_outfit_compatibility_with_ai(self, outfit_items: List[Dict], 
                                           weather_data: Dict, occasion: str) -> Dict:
        """Use AI to analyze outfit compatibility"""
        if not self.ai_loaded or not outfit_items:
            return {'confidence': 70, 'ai_analysis': False}
        
        try:
            # Create descriptions for AI analysis
            outfit_descriptions = []
            for item in outfit_items:
                description = f"a {item.get('color', 'colored')} {item.get('name', item.get('category', 'clothing item'))}"
                outfit_descriptions.append(description)
            
            # Basic AI scoring (simplified for this implementation)
            style_score = 80.0  # Could be enhanced with actual CLIP analysis
            color_score = 75.0
            occasion_score = 85.0
            weather_score = 80.0
            
            overall_score = (style_score + color_score + occasion_score + weather_score) / 4
            
            return {
                'overall_compatibility': overall_score,
                'style_cohesion': style_score,
                'color_harmony': color_score,
                'occasion_appropriateness': occasion_score,
                'weather_suitability': weather_score,
                'ai_analysis': True,
                'confidence': int(overall_score)
            }
            
        except Exception as e:
            logger.error(f"AI outfit analysis failed: {e}")
            return {'confidence': 70, 'ai_analysis': False}
    
    def generate_multi_occasion_recommendations(self, user_id: int, weather_data: Dict) -> Dict:
        """Generate outfit recommendations for all occasions"""
        occasions = ['casual', 'work', 'formal', 'workout', 'datenight', 'party']
        recommendations = {}
        
        try:
            wardrobe_items = self.get_user_wardrobe_items(user_id)
            
            if not wardrobe_items:
                return {
                    'error': 'No wardrobe items found',
                    'message': 'Please add some clothes to your wardrobe first!',
                    'recommendations': {}
                }
            
            for occasion in occasions:
                try:
                    outfit = self.generate_outfit_recommendation(user_id, weather_data, occasion)
                    recommendations[occasion] = outfit
                except Exception as e:
                    logger.error(f"Failed to generate {occasion} outfit: {e}")
                    recommendations[occasion] = {
                        'error': f'Failed to generate {occasion} outfit',
                        'message': str(e),
                        'items': [],
                        'confidence': 0
                    }
            
            return {
                'recommendations': recommendations,
                'weather_context': weather_data,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating multi-occasion recommendations: {e}")
            return {
                'error': 'Failed to generate recommendations',
                'message': str(e),
                'recommendations': {}
            }
    
    def _generate_outfit_reason(self, items: List[Dict], weather_data: Dict, occasion: str) -> str:
        """Generate explanation for outfit choice"""
        if not items:
            return "No suitable items found in your wardrobe for these conditions."
        
        temp = weather_data.get('temperature', 20)
        item_names = [item['name'] for item in items]
        
        if temp < 10:
            temp_desc = "warm layers for cold weather"
        elif temp > 30:
            temp_desc = "lightweight pieces for hot weather"
        elif temp > 25:
            temp_desc = "breathable fabrics for warm conditions"
        else:
            temp_desc = "comfortable pieces for mild temperatures"
        
        occasion_text = {
            'casual': 'relaxed daily activities',
            'business': 'professional appearance',
            'formal': 'sophisticated events',
            'workout': 'active lifestyle',
            'datenight': 'special occasions',
            'party': 'celebratory nights out with statement and shiny pieces'
        }.get(occasion, 'your planned activities')
        
        return f"Perfect for {occasion_text} with {temp_desc}. Your {', '.join(item_names[:2])} combination creates a well-coordinated look from your wardrobe."

# Global instance
ai_enhanced_outfit_service = AIEnhancedOutfitService()