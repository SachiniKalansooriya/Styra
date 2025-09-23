import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class TripAIService:
    """AI-powered trip planning and packing suggestions service"""
    
    def analyze_wardrobe_for_trip(self, wardrobe_items: List[Dict], trip_details: Dict) -> Dict:
        """Analyze wardrobe compatibility with trip requirements"""
        
        activities = trip_details.get('activities', [])
        weather = trip_details.get('weatherExpected', '').lower()
        destination = trip_details.get('destination', '').lower()
        
        analysis = {
            'categories_coverage': {},
            'activity_readiness': {},
            'weather_preparedness': {},
            'destination_suitability': {},
            'gaps': [],
            'recommendations': []
        }
        
        # Categorize existing wardrobe
        categories = self._categorize_wardrobe_items(wardrobe_items)
        
        # Analyze category coverage
        analysis['categories_coverage'] = self._analyze_category_coverage(categories)
        
        # Activity readiness analysis
        analysis['activity_readiness'] = self._analyze_activity_readiness(wardrobe_items, activities)
        
        # Weather preparedness
        analysis['weather_preparedness'] = self._analyze_weather_preparedness(wardrobe_items, weather)
        
        # Destination suitability
        analysis['destination_suitability'] = self._analyze_destination_suitability(destination)
        
        # Generate gaps and recommendations
        analysis['gaps'], analysis['recommendations'] = self._generate_gaps_and_recommendations(analysis)
        
        return analysis
    
    def generate_enhanced_trip_recommendations(self, trip_details: Dict, wardrobe_analysis: Dict, duration: int) -> List[Dict]:
        """Generate intelligent trip recommendations with AI analysis"""
        
        activities = trip_details.get('activities', [])
        weather = trip_details.get('weatherExpected', '').lower()
        packing_style = trip_details.get('packingStyle', 'comfort')
        destination = trip_details.get('destination', '').lower()
        
        recommendations = []
        
        # Base clothing recommendations
        base_clothing = self._calculate_smart_base_clothing(duration, packing_style, activities)
        recommendations.append({
            'category': 'Essential Clothing',
            'items': base_clothing,
            'priority': 'high',
            'reasoning': f'Basic clothing needs for {duration} day trip with {packing_style} style preference'
        })
        
        # Activity-specific recommendations
        activity_items = self._get_detailed_activity_items(activities, wardrobe_analysis)
        if activity_items:
            recommendations.append({
                'category': 'Activity Specific',
                'items': activity_items,
                'priority': 'medium',
                'reasoning': 'Items needed for your planned activities'
            })
        
        # Weather-specific recommendations
        weather_items = self._get_detailed_weather_items(weather, wardrobe_analysis)
        if weather_items:
            recommendations.append({
                'category': 'Weather Protection',
                'items': weather_items,
                'priority': 'high',
                'reasoning': f'Weather-appropriate items for {weather} conditions'
            })
        
        # Destination-specific recommendations
        destination_items = self._get_destination_items(destination)
        if destination_items:
            recommendations.append({
                'category': 'Destination Specific',
                'items': destination_items,
                'priority': 'medium',
                'reasoning': f'Items commonly needed for {destination} destinations'
            })
        
        # Travel essentials
        essentials = self._get_travel_essentials()
        recommendations.append({
            'category': 'Travel Essentials',
            'items': essentials,
            'priority': 'critical',
            'reasoning': 'Essential items for any trip'
        })
        
        # Shopping suggestions based on wardrobe gaps
        shopping_items = self._generate_shopping_suggestions(wardrobe_analysis, activities, weather)
        if shopping_items:
            recommendations.append({
                'category': 'Shopping Suggestions',
                'items': shopping_items,
                'priority': 'low',
                'reasoning': 'Items you might want to buy to enhance your trip experience'
            })
        
        return recommendations
    
    def find_detailed_wardrobe_matches(self, recommendations: List[Dict], wardrobe_items: List[Dict]) -> Dict:
        """Find specific wardrobe items that match recommendations"""
        
        matches = {}
        
        for rec_category in recommendations:
            category_name = rec_category['category']
            matches[category_name] = []
            
            for item in rec_category['items']:
                item_name = item.get('name', '') if isinstance(item, dict) else str(item)
                matching_items = self._find_matching_wardrobe_items(item_name, wardrobe_items)
                
                matches[category_name].append({
                    'recommendation': item_name,
                    'matches': matching_items[:3],  # Top 3 matches
                    'status': 'available' if matching_items else 'needed'
                })
        
        return matches
    
    def calculate_detailed_wardrobe_coverage(self, wardrobe_items: List[Dict], recommendations: List[Dict]) -> Dict:
        """Calculate how much of the trip needs can be covered by existing wardrobe"""
        
        total_recommendations = sum(len(rec.get('items', [])) for rec in recommendations 
                                  if rec.get('category') != 'Shopping Suggestions')
        
        if total_recommendations == 0:
            return {'percentage': 100, 'covered_count': 0, 'total_count': 0}
        
        covered_count = 0
        
        for rec_category in recommendations:
            if rec_category.get('category') == 'Shopping Suggestions':
                continue
                
            for item in rec_category.get('items', []):
                item_name = item.get('name', '') if isinstance(item, dict) else str(item)
                if self._has_suitable_wardrobe_match(item_name, wardrobe_items):
                    covered_count += 1
        
        coverage_percentage = (covered_count / total_recommendations) * 100
        
        return {
            'percentage': round(coverage_percentage, 1),
            'covered_count': covered_count,
            'total_count': total_recommendations,
            'status': self._get_coverage_status(coverage_percentage)
        }
    
    # Private helper methods
    
    def _categorize_wardrobe_items(self, wardrobe_items: List[Dict]) -> Dict:
        """Categorize wardrobe items by category"""
        categories = {}
        for item in wardrobe_items:
            category = item.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories
    
    def _analyze_category_coverage(self, categories: Dict) -> Dict:
        """Analyze coverage of essential clothing categories"""
        essential_categories = ['tops', 'bottoms', 'shoes', 'accessories', 'outerwear']
        coverage = {}
        
        for category in essential_categories:
            count = len(categories.get(category, []))
            coverage[category] = {
                'count': count,
                'adequacy': (
                    'excellent' if count >= 5 else
                    'good' if count >= 3 else
                    'limited' if count >= 1 else
                    'missing'
                )
            }
        
        return coverage
    
    def _analyze_activity_readiness(self, wardrobe_items: List[Dict], activities: List[str]) -> Dict:
        """Analyze readiness for specific activities"""
        
        activity_requirements = {
            'Business Meetings': {
                'required_items': ['formal', 'business', 'suit', 'dress', 'professional'],
                'categories': ['tops', 'bottoms', 'shoes', 'accessories']
            },
            'Beach/Pool': {
                'required_items': ['swimwear', 'swim', 'beach', 'casual', 'sandals'],
                'categories': ['accessories', 'shoes']
            },
            'Hiking/Outdoor': {
                'required_items': ['athletic', 'sport', 'outdoor', 'hiking', 'walking'],
                'categories': ['tops', 'bottoms', 'shoes']
            },
            'Fine Dining': {
                'required_items': ['formal', 'elegant', 'dress', 'nice', 'dressy'],
                'categories': ['tops', 'bottoms', 'shoes', 'accessories']
            },
            'Nightlife': {
                'required_items': ['party', 'dressy', 'going out', 'nice', 'evening'],
                'categories': ['tops', 'bottoms', 'shoes', 'accessories']
            }
        }
        
        readiness = {}
        
        for activity in activities:
            if activity in activity_requirements:
                req = activity_requirements[activity]
                suitable_items = []
                
                for item in wardrobe_items:
                    item_text = (
                        item.get('name', '') + ' ' + 
                        item.get('season', '') + ' ' + 
                        item.get('category', '')
                    ).lower()
                    
                    if any(keyword in item_text for keyword in req['required_items']):
                        suitable_items.append(item)
                
                readiness[activity] = {
                    'suitable_items': len(suitable_items),
                    'items': suitable_items[:3],
                    'readiness': (
                        'excellent' if len(suitable_items) >= 3 else
                        'good' if len(suitable_items) >= 2 else
                        'partial' if len(suitable_items) >= 1 else
                        'unprepared'
                    )
                }
        
        return readiness
    
    def _analyze_weather_preparedness(self, wardrobe_items: List[Dict], weather: str) -> Dict:
        """Analyze preparedness for weather conditions"""
        
        weather_conditions = {
            'cold': ['cold', 'winter', 'snow', 'freezing'],
            'hot': ['hot', 'summer', 'warm', 'sunny'],
            'rain': ['rain', 'wet', 'storm'],
            'tropical': ['humid', 'tropical']
        }
        
        preparedness = {}
        
        for condition, keywords in weather_conditions.items():
            if any(keyword in weather for keyword in keywords):
                suitable_items = []
                
                if condition == 'cold':
                    suitable_items = [
                        item for item in wardrobe_items 
                        if (item.get('category') == 'outerwear' or 
                            'warm' in item.get('name', '').lower() or
                            'winter' in item.get('season', '').lower())
                    ]
                elif condition == 'hot':
                    suitable_items = [
                        item for item in wardrobe_items 
                        if ('light' in item.get('name', '').lower() or
                            'summer' in item.get('season', '').lower() or
                            item.get('color', '').lower() in ['white', 'light', 'beige'])
                    ]
                elif condition == 'rain':
                    suitable_items = [
                        item for item in wardrobe_items 
                        if ('rain' in item.get('name', '').lower() or
                            'waterproof' in item.get('name', '').lower())
                    ]
                
                preparedness[condition] = {
                    'suitable_items': len(suitable_items),
                    'items': suitable_items[:3],
                    'prepared': len(suitable_items) >= 1
                }
        
        return preparedness
    
    def _analyze_destination_suitability(self, destination: str) -> Dict:
        """Analyze suitability for destination type"""
        
        destination_keywords = {
            'beach': ['beach', 'tropical', 'island', 'resort'],
            'city': ['city', 'urban', 'metropolitan'],
            'mountain': ['mountain', 'alpine', 'hiking'],
            'business': ['business', 'corporate', 'conference']
        }
        
        suitability = {}
        
        for dest_type, keywords in destination_keywords.items():
            if any(keyword in destination for keyword in keywords):
                suitability[dest_type] = True
        
        return suitability
    
    def _generate_gaps_and_recommendations(self, analysis: Dict) -> tuple:
        """Generate gaps and recommendations based on analysis"""
        
        gaps = []
        recommendations = []
        
        for category, info in analysis['categories_coverage'].items():
            if info['adequacy'] == 'missing':
                gaps.append(f"No {category} in wardrobe")
                recommendations.append(f"Consider adding {category} to your wardrobe")
            elif info['adequacy'] == 'limited':
                gaps.append(f"Limited {category} options")
                recommendations.append(f"More variety in {category} would be helpful")
        
        return gaps, recommendations
    
    def _calculate_smart_base_clothing(self, duration: int, style: str, activities: List[str]) -> List[Dict]:
        """Calculate base clothing needs with AI considerations"""
        
        style_multipliers = {
            'minimal': {'tops': 0.6, 'bottoms': 0.4, 'underwear': 1.0, 'shoes': 1},
            'comfort': {'tops': 0.8, 'bottoms': 0.5, 'underwear': 1.1, 'shoes': 1.5},
            'fashion': {'tops': 1.2, 'bottoms': 0.8, 'underwear': 1.2, 'shoes': 2.5},
            'business': {'tops': 1.0, 'bottoms': 0.7, 'underwear': 1.1, 'shoes': 2}
        }
        
        multiplier = style_multipliers.get(style, style_multipliers['comfort'])
        
        # Adjust based on activities
        activity_adjustment = 1.0
        if 'Business Meetings' in activities:
            activity_adjustment += 0.3
        if any(activity in activities for activity in ['Hiking/Outdoor', 'Sports/Exercise']):
            activity_adjustment += 0.2
        
        tops_needed = max(2, int(duration * multiplier['tops'] * activity_adjustment))
        bottoms_needed = max(2, int(duration * multiplier['bottoms'] * activity_adjustment))
        underwear_needed = int((duration + 1) * multiplier['underwear'])
        shoes_needed = max(1, int(multiplier['shoes']))
        
        items = [
            {'name': f"{tops_needed} tops/shirts", 'quantity': tops_needed, 'status': 'needed', 'category': 'tops'},
            {'name': f"{bottoms_needed} bottoms/pants", 'quantity': bottoms_needed, 'status': 'needed', 'category': 'bottoms'},
            {'name': f"{underwear_needed} underwear", 'quantity': underwear_needed, 'status': 'needed', 'category': 'underwear'},
            {'name': f"{underwear_needed} socks", 'quantity': underwear_needed, 'status': 'needed', 'category': 'socks'},
            {'name': f"{shoes_needed} pairs of shoes", 'quantity': shoes_needed, 'status': 'needed', 'category': 'shoes'}
        ]
        
        return items
    
    def _get_detailed_activity_items(self, activities: List[str], wardrobe_analysis: Dict) -> List[Dict]:
        """Get detailed activity-specific items with wardrobe awareness"""
        
        activity_map = {
            'Business Meetings': [
                {'name': 'Business suit or formal attire', 'status': 'required', 'category': 'formal'},
                {'name': 'Dress shoes', 'status': 'required', 'category': 'shoes'},
                {'name': 'Belt', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Business bag or briefcase', 'status': 'recommended', 'category': 'accessories'}
            ],
            'Beach/Pool': [
                {'name': 'Swimwear', 'status': 'required', 'category': 'swimwear'},
                {'name': 'Beach towel', 'status': 'required', 'category': 'accessories'},
                {'name': 'Sandals or flip-flops', 'status': 'required', 'category': 'shoes'},
                {'name': 'Sun hat', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Sunscreen', 'status': 'required', 'category': 'care'}
            ],
            'Hiking/Outdoor': [
                {'name': 'Hiking boots or sturdy shoes', 'status': 'required', 'category': 'shoes'},
                {'name': 'Moisture-wicking clothes', 'status': 'recommended', 'category': 'tops'},
                {'name': 'Backpack', 'status': 'required', 'category': 'accessories'},
                {'name': 'Water bottle', 'status': 'required', 'category': 'accessories'}
            ],
            'Fine Dining': [
                {'name': 'Formal outfit', 'status': 'required', 'category': 'formal'},
                {'name': 'Dress shoes', 'status': 'required', 'category': 'shoes'},
                {'name': 'Nice accessories', 'status': 'recommended', 'category': 'accessories'}
            ],
            'Nightlife': [
                {'name': 'Party or dressy outfit', 'status': 'required', 'category': 'party'},
                {'name': 'Dressy shoes', 'status': 'required', 'category': 'shoes'},
                {'name': 'Statement accessories', 'status': 'recommended', 'category': 'accessories'}
            ],
            'City Sightseeing': [
                {'name': 'Comfortable walking shoes', 'status': 'required', 'category': 'shoes'},
                {'name': 'Lightweight jacket', 'status': 'recommended', 'category': 'outerwear'},
                {'name': 'Crossbody bag or daypack', 'status': 'recommended', 'category': 'accessories'}
            ]
        }
        
        items = []
        for activity in activities:
            if activity in activity_map:
                activity_items = activity_map[activity]
                for item in activity_items:
                    readiness = wardrobe_analysis.get('activity_readiness', {}).get(activity, {}).get('readiness', 'unprepared')
                    if readiness in ['ready', 'good', 'excellent']:
                        item['status'] = 'available'
                    items.append(item)
        
        return self._remove_duplicate_items(items)
    
    def _get_detailed_weather_items(self, weather: str, wardrobe_analysis: Dict) -> List[Dict]:
        """Get detailed weather-specific items with wardrobe awareness"""
        
        items = []
        
        weather_items_map = {
            'cold': [
                {'name': 'Warm coat or winter jacket', 'status': 'required', 'category': 'outerwear'},
                {'name': 'Gloves', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Scarf', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Warm hat or beanie', 'status': 'recommended', 'category': 'accessories'}
            ],
            'hot': [
                {'name': 'Sunglasses', 'status': 'required', 'category': 'accessories'},
                {'name': 'Sun hat', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Light, breathable fabrics', 'status': 'required', 'category': 'tops'},
                {'name': 'Sunscreen', 'status': 'required', 'category': 'care'}
            ],
            'rain': [
                {'name': 'Rain jacket or waterproof coat', 'status': 'required', 'category': 'outerwear'},
                {'name': 'Umbrella', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Waterproof shoes', 'status': 'recommended', 'category': 'shoes'}
            ]
        }
        
        for condition, condition_items in weather_items_map.items():
            if any(keyword in weather for keyword in [condition]):
                preparedness = wardrobe_analysis.get('weather_preparedness', {}).get(condition, {})
                for item in condition_items:
                    if preparedness.get('prepared', False):
                        item['status'] = 'available'
                    items.extend(condition_items)
                break
        
        return items
    
    def _get_destination_items(self, destination: str) -> List[Dict]:
        """Get destination-specific items"""
        
        destination_items = {
            'beach': [
                {'name': 'Beach umbrella', 'status': 'recommended', 'category': 'accessories'},
                {'name': 'Waterproof bag', 'status': 'recommended', 'category': 'accessories'}
            ],
            'city': [
                {'name': 'Portable phone charger', 'status': 'recommended', 'category': 'electronics'},
                {'name': 'City map or guidebook', 'status': 'recommended', 'category': 'accessories'}
            ],
            'mountain': [
                {'name': 'First aid kit', 'status': 'recommended', 'category': 'safety'},
                {'name': 'Headlamp or flashlight', 'status': 'recommended', 'category': 'accessories'}
            ]
        }
        
        items = []
        for dest_type, dest_items in destination_items.items():
            if dest_type in destination.lower():
                items.extend(dest_items)
        
        return items
    
    def _get_travel_essentials(self) -> List[Dict]:
        """Get essential travel items"""
        
        return [
            {'name': 'Passport/ID documents', 'status': 'required', 'category': 'documents'},
            {'name': 'Phone charger', 'status': 'required', 'category': 'electronics'},
            {'name': 'Toiletries kit', 'status': 'required', 'category': 'personal_care'},
            {'name': 'Medications', 'status': 'required', 'category': 'health'},
            {'name': 'Travel insurance documents', 'status': 'recommended', 'category': 'documents'}
        ]
    
    def _generate_shopping_suggestions(self, wardrobe_analysis: Dict, activities: List[str], weather: str) -> List[Dict]:
        """Generate shopping suggestions based on wardrobe gaps"""
        
        suggestions = []
        
        # Check for category gaps
        for category, info in wardrobe_analysis.get('categories_coverage', {}).items():
            if info['adequacy'] in ['missing', 'limited']:
                suggestions.append({
                    'name': f"More {category} items",
                    'status': 'suggested',
                    'category': category,
                    'reason': f"Limited {category} in wardrobe"
                })
        
        # Check activity readiness
        for activity, readiness in wardrobe_analysis.get('activity_readiness', {}).items():
            if readiness['readiness'] == 'unprepared':
                suggestions.append({
                    'name': f"Attire for {activity}",
                    'status': 'suggested',
                    'category': 'activity',
                    'reason': f"No suitable items for {activity}"
                })
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _find_matching_wardrobe_items(self, recommendation: str, wardrobe_items: List[Dict]) -> List[Dict]:
        """Find wardrobe items that match a recommendation"""
        
        rec_lower = recommendation.lower()
        matching_items = []
        
        for item in wardrobe_items:
            item_text = (
                item.get('name', '') + ' ' + 
                item.get('category', '') + ' ' + 
                item.get('color', '')
            ).lower()
            
            # Calculate match confidence
            confidence = self._calculate_match_confidence(rec_lower, item_text)
            
            if confidence > 0.1:  # Minimum threshold
                matching_items.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'category': item.get('category'),
                    'color': item.get('color'),
                    'image_url': item.get('image_url'),
                    'confidence': confidence
                })
        
        # Sort by confidence and return top matches
        return sorted(matching_items, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_match_confidence(self, recommendation: str, item_text: str) -> float:
        """Calculate match confidence between recommendation and item"""
        
        rec_words = set(recommendation.split())
        item_words = set(item_text.split())
        
        if not rec_words or not item_words:
            return 0.0
        
        # Jaccard similarity
        intersection = len(rec_words.intersection(item_words))
        union = len(rec_words.union(item_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _has_suitable_wardrobe_match(self, recommendation: str, wardrobe_items: List[Dict]) -> bool:
        """Check if recommendation has suitable wardrobe matches"""
        
        matches = self._find_matching_wardrobe_items(recommendation, wardrobe_items)
        return len(matches) > 0 and matches[0]['confidence'] > 0.2
    
    def _get_coverage_status(self, percentage: float) -> str:
        """Get coverage status based on percentage"""
        
        if percentage >= 80:
            return 'excellent'
        elif percentage >= 60:
            return 'good'
        elif percentage >= 40:
            return 'moderate'
        else:
            return 'low'
    
    def _remove_duplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items while preserving order"""
        
        seen = set()
        unique_items = []
        
        for item in items:
            item_key = item.get('name', '')
            if item_key not in seen:
                seen.add(item_key)
                unique_items.append(item)
        
        return unique_items

# Create global instance
trip_ai_service = TripAIService()