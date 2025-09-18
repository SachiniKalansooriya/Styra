# services/enhanced_outfit_service.py
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from datetime import datetime
import uuid
import logging
from typing import Dict, List, Optional
from database.connection import db

logger = logging.getLogger(__name__)

class EnhancedOutfitService:
    def __init__(self):
        self.weather_compatibility_matrix = self._create_weather_compatibility_matrix()
        self.color_harmony_rules = self._create_color_harmony_rules()
        self.outfit_rules = self._create_outfit_rules()
    
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
                },
                'bottoms': {
                    'very_cold': {'jeans': 8, 'pants': 9, 'leggings': 7, 'shorts': 1},
                    'cold': {'jeans': 9, 'pants': 8, 'leggings': 8, 'shorts': 2},
                    'cool': {'jeans': 7, 'pants': 7, 'leggings': 6, 'shorts': 4},
                    'mild': {'jeans': 6, 'pants': 6, 'leggings': 5, 'shorts': 8},
                    'warm': {'shorts': 9, 'light_pants': 7, 'skirt': 8, 'jeans': 4},
                    'hot': {'shorts': 10, 'skirt': 9, 'light_pants': 6, 'jeans': 2}
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
            'cool_colors': ['blue', 'green', 'purple', 'teal', 'navy', 'turquoise'],
            'seasonal_palettes': {
                'spring': ['light_blue', 'pink', 'yellow', 'green', 'coral'],
                'summer': ['navy', 'white', 'light_blue', 'pink', 'purple'],
                'fall': ['brown', 'orange', 'burgundy', 'olive', 'cream'],
                'winter': ['black', 'white', 'red', 'navy', 'gray']
            }
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
                'datenight': (6, 9)
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
                'business': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes', 'outerwear'],
                    'preferred_items': ['button shirt', 'blouse', 'dress pants', 'blazer', 'dress shoes'],
                    'color_preferences': ['navy', 'black', 'white', 'gray', 'brown'],
                    'avoid_items': ['tank top', 'shorts', 'sneakers', 'flip-flops']
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
                },
                'date': {
                    'preferred_categories': ['tops', 'bottoms', 'shoes', 'accessories'],
                    'preferred_items': ['dress', 'nice top', 'blouse', 'nice pants', 'dress shoes'],
                    'color_preferences': ['red', 'black', 'blue', 'white', 'pink'],
                    'avoid_items': ['workout', 'athletic', 'gym clothes']
                },
                'datenight': {
                    'preferred_categories': ['dresses', 'tops', 'bottoms', 'shoes', 'accessories'],
                    'preferred_items': ['dress', 'frock', 'nice top', 'blouse', 'crop top', 'denim', 'jeans', 'cute pants', 'heels', 'flats', 'boots'],
                    'color_preferences': ['red', 'black', 'blue', 'white', 'pink', 'burgundy', 'navy'],
                    'avoid_items': ['workout', 'athletic', 'gym clothes', 'office trousers', 'formal pants', 'dress pants', 'blazer', 'business shirt']
                }
            },
            'category_combinations': {
                'required': ['tops', 'bottoms'],
                'optional': ['shoes', 'outerwear', 'accessories'],
                'avoid_combinations': [
                    ('tank_top', 'formal_pants'),
                    ('dress_shirt', 'athletic_shorts'),
                    ('hoodie', 'dress_pants'),
                    ('workout_top', 'dress_pants'),
                    ('formal_dress', 'sneakers')
                ]
            }
        }
    
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
                    
                    # Add AI scoring attributes based on category
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
            'tank_top': [25, 40],
            't_shirt': [18, 35],
            'blouse': [16, 30],
            'sweater': [5, 20],
            'hoodie': [8, 25],
            'jacket': [0, 18],
            'shorts': [22, 40],
            'pants': [5, 30],
            'jeans': [8, 25],
            'skirt': [20, 35],
            'dress': [15, 32]
        }
        
        # Adjust based on season
        season_adjustments = {
            'winter': [-5, -10],
            'summer': [5, 10],
            'spring': [0, 5],
            'fall': [-2, -5]
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
            'business': 7, 'office': 7, 'professional': 7, 'blouse': 7,
            'polo': 6, 'chinos': 6, 'loafers': 6, 'cardigan': 6
        }
        
        # Datenight appropriate items (mid-formal range)
        datenight_keywords = {
            'dress': 6, 'frock': 6, 'nice dress': 7, 'party dress': 6,
            'denim': 5, 'jeans': 5, 'cute top': 5, 'nice top': 6,
            'crop top': 4, 'heels': 7, 'boots': 5, 'flats': 5
        }
        
        casual_keywords = {
            't-shirt': 2, 'tank top': 1, 'hoodie': 2, 'sweatshirt': 2,
            'shorts': 2, 'athletic': 1, 'gym': 1, 'workout': 1, 'sport': 1,
            'sneakers': 3, 'flip-flops': 1, 'sandals': 2, 'running': 1,
            'yoga': 1, 'joggers': 2, 'leggings': 2
        }
        
        name_lower = name.lower()
        category_lower = category.lower()
        combined_text = f"{name_lower} {category_lower}"
        
        # Check for formal keywords first (higher priority)
        max_formal_score = 0
        for keyword, score in formal_keywords.items():
            if keyword in combined_text:
                max_formal_score = max(max_formal_score, score)
        
        if max_formal_score > 0:
            return max_formal_score
        
        # Check for datenight appropriate items
        max_datenight_score = 0
        for keyword, score in datenight_keywords.items():
            if keyword in combined_text:
                max_datenight_score = max(max_datenight_score, score)
        
        if max_datenight_score > 0:
            return max_datenight_score
        
        # Check for casual keywords
        min_casual_score = 10
        for keyword, score in casual_keywords.items():
            if keyword in combined_text:
                min_casual_score = min(min_casual_score, score)
        
        if min_casual_score < 10:
            return min_casual_score
        
        # Category-based defaults if no keywords match
        category_defaults = {
            'formal': 8,
            'dress': 6,  # Updated for datenight compatibility
            'dresses': 6,  # Updated for datenight compatibility
            'tops': 5,
            'bottoms': 5,
            'shoes': 5,
            'outerwear': 6,
            'sportswear': 2,
            'athletic': 1
        }
        
        for cat, score in category_defaults.items():
            if cat in category_lower:
                return score
        
        return 5  # Default middle score
    
    def _get_comfort_score(self, category: str) -> int:
        """Estimate comfort score 1-10"""
        comfort_scores = {
            'athletic': 10,
            'casual': 8,
            'lounge': 9,
            'business': 6,
            'formal': 4
        }
        
        category_lower = category.lower()
        for key, score in comfort_scores.items():
            if key in category_lower:
                return score
        
        return 7  # Default
    
    def _get_weather_compatibility(self, category: str) -> List[str]:
        """Get weather conditions this item is good for"""
        compatibility_map = {
            'tank_top': ['sunny', 'hot'],
            't_shirt': ['sunny', 'cloudy', 'mild'],
            'sweater': ['cloudy', 'cold', 'windy'],
            'hoodie': ['cloudy', 'cool', 'windy'],
            'jacket': ['cold', 'windy', 'rainy'],
            'shorts': ['sunny', 'hot', 'warm'],
            'pants': ['cloudy', 'cool', 'cold'],
            'jeans': ['cloudy', 'cool', 'casual']
        }
        
        category_lower = category.lower()
        return compatibility_map.get(category_lower, ['sunny', 'cloudy'])
    
    def calculate_item_compatibility_score(self, item: Dict, weather_data: Dict, 
                                         occasion: str) -> float:
        """Calculate enhanced AI compatibility score for clothing item"""
        score = 0.0
        
        # Temperature compatibility (35% weight)
        temp = weather_data.get('temperature', 20)
        temp_min, temp_max = item['temp_range']
        if temp_min <= temp <= temp_max:
            temp_score = 35.0
            # Bonus for optimal range
            optimal_temp = (temp_min + temp_max) / 2
            temp_distance = abs(temp - optimal_temp)
            if temp_distance <= 3:  # Within 3 degrees of optimal
                temp_score += 5.0
        else:
            # Penalty for being outside range
            temp_distance = min(abs(temp - temp_min), abs(temp - temp_max))
            temp_score = max(0, 35.0 - (temp_distance * 2))
        
        score += temp_score
        
        # Occasion matching (35% weight - increased importance)
        occasion_formality_range = self.outfit_rules['occasion_formality'].get(occasion, (1, 10))
        item_formality = item['formality_score']
        
        if occasion_formality_range[0] <= item_formality <= occasion_formality_range[1]:
            occasion_score = 35.0
        else:
            # Penalty based on how far outside the range
            if item_formality < occasion_formality_range[0]:
                penalty = (occasion_formality_range[0] - item_formality) * 4
            else:
                penalty = (item_formality - occasion_formality_range[1]) * 4
            occasion_score = max(0, 35.0 - penalty)
        
        # Bonus for occasion-specific preferred items
        occasion_rules = self.outfit_rules.get('occasion_specific_rules', {}).get(occasion, {})
        preferred_items = occasion_rules.get('preferred_items', [])
        avoid_items = occasion_rules.get('avoid_items', [])
        
        item_name_lower = item.get('name', '').lower()
        item_category_lower = item.get('category', '').lower()
        
        # Check for preferred items bonus
        for preferred in preferred_items:
            if preferred in item_name_lower or preferred in item_category_lower:
                occasion_score += 5.0
                break
        
        # Check for avoided items penalty
        for avoided in avoid_items:
            if avoided in item_name_lower or avoided in item_category_lower:
                occasion_score -= 10.0
                break
        
        score += max(occasion_score, 0)
        
        # Weather condition compatibility (15% weight)
        weather_conditions = self._extract_weather_conditions(weather_data)
        weather_score = 0
        for condition in weather_conditions:
            if condition in item['weather_compatibility']:
                weather_score += 15.0 / len(weather_conditions)
        
        score += min(weather_score, 15.0)
        
        # Color preference for occasion (10% weight)
        color_score = self._calculate_color_preference_score(item, occasion)
        score += color_score
        
        # Comfort and versatility (5% weight)
        comfort_score = (item['comfort_score'] / 10) * 5.0
        score += comfort_score
        
        return min(score, 100.0)
    
    def _calculate_color_preference_score(self, item: Dict, occasion: str) -> float:
        """Calculate color preference score for the occasion"""
        occasion_rules = self.outfit_rules.get('occasion_specific_rules', {}).get(occasion, {})
        preferred_colors = occasion_rules.get('color_preferences', [])
        
        if not preferred_colors:
            return 5.0  # Default score if no preferences
        
        item_color = item.get('color', '').lower()
        
        # Direct color match
        for preferred_color in preferred_colors:
            if preferred_color.lower() in item_color or item_color in preferred_color.lower():
                return 10.0
        
        # Neutral colors work for most occasions
        neutral_colors = self.color_harmony_rules['neutral_colors']
        if any(neutral in item_color for neutral in neutral_colors):
            return 7.0
        
        return 3.0  # Non-preferred color penalty
    
    def _extract_weather_conditions(self, weather_data: Dict) -> List[str]:
        """Extract weather conditions from weather data"""
        conditions = []
        
        temp = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        wind_speed = weather_data.get('windSpeed', 0)
        precipitation = weather_data.get('precipitation', 0)
        condition = weather_data.get('condition', '').lower()
        
        # Temperature-based conditions
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
        
        # Weather-based conditions
        if 'sun' in condition or 'clear' in condition:
            conditions.append('sunny')
        elif 'cloud' in condition:
            conditions.append('cloudy')
        elif 'rain' in condition or precipitation > 0.5:
            conditions.append('rainy')
        
        if wind_speed > 20:
            conditions.append('windy')
        if humidity > 70:
            conditions.append('humid')
        
        return conditions
    
    def generate_outfit_recommendation(self, user_id: int, weather_data: Dict, 
                                     occasion: str) -> Dict:
        """Generate AI outfit recommendation using user's actual wardrobe"""
        try:
            # Get user's wardrobe items
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
                
                # Sort by score
                scored_items[category].sort(key=lambda x: x[1], reverse=True)
            
            # Build outfit
            outfit_items = []
            total_score = 0
            score_count = 0
            
            # Required categories
            required_categories = ['tops', 'bottoms']
            for req_cat in required_categories:
                # Try different category variations
                possible_cats = [req_cat, req_cat[:-1]]  # 'tops' -> 'top'
                found_item = None
                
                for cat_variant in possible_cats:
                    if cat_variant in scored_items and scored_items[cat_variant]:
                        found_item = scored_items[cat_variant][0]  # Get top scored item
                        break
                
                if found_item:
                    outfit_items.append(found_item[0])
                    total_score += found_item[1]
                    score_count += 1
            
            # Optional categories (shoes, outerwear)
            optional_categories = ['shoes', 'outerwear', 'accessories']
            for opt_cat in optional_categories:
                if opt_cat in scored_items and scored_items[opt_cat]:
                    # Add shoes if available
                    if opt_cat == 'shoes':
                        outfit_items.append(scored_items[opt_cat][0][0])
                        total_score += scored_items[opt_cat][0][1]
                        score_count += 1
                    # Add outerwear if weather requires it
                    elif opt_cat == 'outerwear':
                        temp = weather_data.get('temperature', 20)
                        if temp < 15 or 'rain' in weather_data.get('condition', '').lower():
                            outfit_items.append(scored_items[opt_cat][0][0])
                            total_score += scored_items[opt_cat][0][1]
                            score_count += 1
            
            # Calculate overall confidence
            confidence = int(total_score / score_count) if score_count > 0 else 50
            
            # Generate outfit reason
            reason = self._generate_outfit_reason(outfit_items, weather_data, occasion)
            
            outfit = {
                'id': f'user_outfit_{uuid.uuid4().hex[:8]}',
                'items': outfit_items,
                'confidence': confidence,
                'reason': reason,
                'weather_context': weather_data,
                'occasion': occasion,
                'generated_at': datetime.now().isoformat()
            }
            
            return outfit
            
        except Exception as e:
            logger.error(f"Error generating outfit recommendation: {e}")
            return {
                'error': 'Failed to generate recommendation',
                'message': str(e)
            }
    
    def generate_multi_occasion_recommendations(self, user_id: int, weather_data: Dict) -> Dict:
        """Generate outfit recommendations for all occasions"""
        occasions = ['casual', 'work', 'formal', 'workout', 'datenight']
        recommendations = {}
        
        try:
            # Get user's wardrobe items once
            wardrobe_items = self.get_user_wardrobe_items(user_id)
            
            if not wardrobe_items:
                return {
                    'error': 'No wardrobe items found',
                    'message': 'Please add some clothes to your wardrobe first!',
                    'recommendations': {}
                }
            
            # Generate recommendation for each occasion
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
            
            # Calculate overall wardrobe analysis
            analysis = self._analyze_wardrobe_for_occasions(wardrobe_items, recommendations)
            
            return {
                'recommendations': recommendations,
                'wardrobe_analysis': analysis,
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
    
    def _analyze_wardrobe_for_occasions(self, wardrobe_items: List[Dict], 
                                      recommendations: Dict) -> Dict:
        """Analyze wardrobe completeness for different occasions"""
        analysis = {
            'total_items': len(wardrobe_items),
            'categories_available': list(set(item['category'].lower() for item in wardrobe_items)),
            'occasion_readiness': {},
            'recommendations_quality': {},
            'wardrobe_gaps': []
        }
        
        # Analyze readiness for each occasion
        for occasion, outfit in recommendations.items():
            if not outfit.get('error'):
                confidence = outfit.get('confidence', 0)
                item_count = len(outfit.get('items', []))
                
                analysis['occasion_readiness'][occasion] = {
                    'confidence': confidence,
                    'item_count': item_count,
                    'status': 'excellent' if confidence > 85 else 'good' if confidence > 70 else 'fair' if confidence > 50 else 'poor'
                }
                
                analysis['recommendations_quality'][occasion] = confidence
            else:
                analysis['occasion_readiness'][occasion] = {
                    'confidence': 0,
                    'item_count': 0,
                    'status': 'unavailable'
                }
                analysis['recommendations_quality'][occasion] = 0
        
        # Identify wardrobe gaps
        occasion_rules = self.outfit_rules.get('occasion_specific_rules', {})
        for occasion, rules in occasion_rules.items():
            if occasion in recommendations:
                outfit = recommendations[occasion]
                if outfit.get('error') or outfit.get('confidence', 0) < 60:
                    preferred_items = rules.get('preferred_items', [])
                    missing_items = []
                    
                    for preferred in preferred_items[:3]:  # Check top 3 preferred items
                        found = any(preferred in item.get('name', '').lower() or 
                                  preferred in item.get('category', '').lower() 
                                  for item in wardrobe_items)
                        if not found:
                            missing_items.append(preferred)
                    
                    if missing_items:
                        analysis['wardrobe_gaps'].append({
                            'occasion': occasion,
                            'missing_items': missing_items
                        })
        
        return analysis
    
    def _generate_outfit_reason(self, items: List[Dict], weather_data: Dict, occasion: str) -> str:
        """Generate explanation for outfit choice"""
        if not items:
            return "No suitable items found in your wardrobe for these conditions."
        
        reasons = []
        temp = weather_data.get('temperature', 20)
        
        # Temperature reasoning
        if temp < 10:
            reasons.append("warm layers for cold weather")
        elif temp > 30:
            reasons.append("lightweight pieces for hot weather")
        elif temp > 25:
            reasons.append("breathable fabrics for warm conditions")
        else:
            reasons.append("comfortable pieces for mild temperatures")
        
        # Occasion reasoning
        occasion_text = {
            'casual': 'relaxed daily activities',
            'business': 'professional appearance',
            'formal': 'sophisticated events',
            'workout': 'active lifestyle',
            'date': 'special occasions'
        }.get(occasion, 'your planned activities')
        
        # Item-specific insights
        item_names = [item['name'] for item in items]
        
        base_reason = f"Perfect for {occasion_text}"
        if reasons:
            base_reason += f" with {', '.join(reasons)}"
        
        base_reason += f". Your {', '.join(item_names[:2])} combination"
        if len(item_names) > 2:
            base_reason += f" with {item_names[2]}"
        
        base_reason += " creates a well-coordinated look from your wardrobe."
        
        return base_reason

# Global instance
enhanced_outfit_service = EnhancedOutfitService()