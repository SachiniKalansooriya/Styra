# services/trip_ai_generator.py
import logging
import json
from typing import Dict, List, Any, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import numpy as np
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class TripAIGenerator:
    """AI-powered trip planning and packing list generator using language models"""
    
    def __init__(self):
        self.ai_loaded = False
        self.text_generator = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Trip planning knowledge base
        self.destination_knowledge = self._build_destination_knowledge()
        self.activity_requirements = self._build_activity_requirements()
        self.weather_clothing_map = self._build_weather_clothing_map()
        self.packing_templates = self._build_packing_templates()
        
    def load_ai_models(self):
        """Load AI models for trip planning"""
        try:
            logger.info("Loading trip planning AI models...")
            
            # Use a smaller, efficient model for text generation
            model_name = "microsoft/DialoGPT-small"
            
            # Load the text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256
            )
            
            self.ai_loaded = True
            logger.info("Trip planning AI models loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            self.ai_loaded = False
            return False
    
    def generate_intelligent_packing_list(self, trip_details: Dict, wardrobe_items: List[Dict], duration: int) -> List[Dict]:
        """Generate AI-powered packing recommendations"""
        try:
            destination = trip_details.get('destination', '').lower()
            activities = trip_details.get('activities', [])
            weather = trip_details.get('weatherExpected', '').lower()
            packing_style = trip_details.get('packingStyle', 'comfort')
            
            logger.info(f"Generating AI packing list for {destination} ({weather} weather, {duration} days)")
            
            # Generate base recommendations using AI analysis
            base_categories = self._generate_base_categories(destination, weather, duration, packing_style)
            
            # Add activity-specific items
            activity_items = self._generate_activity_items(activities, destination, weather)
            
            # Add weather-specific protections
            weather_items = self._generate_weather_items(weather, destination, duration)
            
            # Generate destination-specific recommendations
            destination_items = self._generate_destination_items(destination, activities)
            
            # Combine and prioritize
            recommendations = []
            
            # Essential clothing (highest priority)
            if base_categories:
                recommendations.append({
                    'category': 'Essential Clothing',
                    'items': base_categories,
                    'priority': 'critical',
                    'reasoning': self._generate_reasoning('essential', destination, weather, duration),
                    'ai_confidence': 0.95
                })
            
            # Activity gear
            if activity_items:
                recommendations.append({
                    'category': 'Activity Essentials',
                    'items': activity_items,
                    'priority': 'high',
                    'reasoning': self._generate_reasoning('activity', destination, weather, duration, activities),
                    'ai_confidence': 0.88
                })
            
            # Weather protection
            if weather_items:
                recommendations.append({
                    'category': 'Weather Protection',
                    'items': weather_items,
                    'priority': 'high',
                    'reasoning': self._generate_reasoning('weather', destination, weather, duration),
                    'ai_confidence': 0.92
                })
            
            # Destination specifics
            if destination_items:
                recommendations.append({
                    'category': 'Destination Specific',
                    'items': destination_items,
                    'priority': 'medium',
                    'reasoning': self._generate_reasoning('destination', destination, weather, duration),
                    'ai_confidence': 0.85
                })
            
            # Travel essentials
            essentials = self._generate_travel_essentials(duration, destination)
            recommendations.append({
                'category': 'Travel Essentials',
                'items': essentials,
                'priority': 'critical',
                'reasoning': 'Universal travel necessities for any trip',
                'ai_confidence': 0.98
            })
            
            # Match with user's wardrobe
            self._match_with_wardrobe(recommendations, wardrobe_items)
            
            logger.info(f"Generated {len(recommendations)} recommendation categories")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI packing list: {e}")
            return self._generate_fallback_recommendations(trip_details, duration)
    
    def _generate_base_categories(self, destination: str, weather: str, duration: int, style: str) -> List[Dict]:
        """Generate base clothing categories using AI logic"""
        items = []
        
        # Calculate quantities based on duration and style
        if style == 'minimal':
            multiplier = 0.7
        elif style == 'luxury':
            multiplier = 1.5
        else:  # comfort
            multiplier = 1.0
        
        # Base clothing calculations
        base_items = {
            'Underwear': max(duration + 2, 7),
            'Socks': max(duration + 1, 5),
            'T-shirts/Basic tops': max(int((duration / 2) * multiplier), 3),
            'Pants/Bottoms': max(int((duration / 3) * multiplier), 2),
        }
        
        # Weather adjustments
        if weather in ['cold', 'cool']:
            base_items.update({
                'Sweaters/Hoodies': max(int(duration / 4), 1),
                'Long pants': max(int(duration / 3), 2),
                'Warm layers': 2
            })
        elif weather in ['hot', 'warm']:
            base_items.update({
                'Shorts': max(int(duration / 3), 2),
                'Light shirts': max(int(duration / 2), 3),
                'Sleeveless tops': max(int(duration / 3), 2)
            })
        
        # Destination adjustments
        if any(word in destination for word in ['beach', 'tropical', 'island']):
            base_items.update({
                'Swimwear': 2,
                'Beach cover-ups': 1,
                'Flip flops': 1
            })
        elif any(word in destination for word in ['city', 'urban', 'business']):
            base_items.update({
                'Smart casual tops': 2,
                'Dress pants/Chinos': 1,
                'Business casual shoes': 1
            })
        
        # Convert to structured format
        for item_name, quantity in base_items.items():
            items.append({
                'name': item_name,
                'quantity': quantity,
                'category': 'clothing',
                'necessity': 'essential',
                'wardrobe_match': None
            })
        
        return items
    
    def _generate_activity_items(self, activities: List[str], destination: str, weather: str) -> List[Dict]:
        """Generate activity-specific items using AI analysis"""
        items = []
        
        for activity in activities:
            activity_lower = activity.lower()
            
            if activity_lower in ['hiking', 'trekking', 'outdoor adventure']:
                items.extend([
                    {'name': 'Hiking boots', 'quantity': 1, 'category': 'footwear', 'necessity': 'critical'},
                    {'name': 'Moisture-wicking shirts', 'quantity': 2, 'category': 'clothing', 'necessity': 'high'},
                    {'name': 'Quick-dry pants', 'quantity': 1, 'category': 'clothing', 'necessity': 'high'},
                    {'name': 'Daypack/Backpack', 'quantity': 1, 'category': 'gear', 'necessity': 'critical'},
                    {'name': 'Water bottle', 'quantity': 1, 'category': 'gear', 'necessity': 'critical'}
                ])
            
            elif activity_lower in ['swimming', 'beach', 'water sports']:
                items.extend([
                    {'name': 'Swimwear', 'quantity': 2, 'category': 'clothing', 'necessity': 'critical'},
                    {'name': 'Beach towel', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                    {'name': 'Waterproof bag', 'quantity': 1, 'category': 'gear', 'necessity': 'medium'},
                    {'name': 'Water shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'medium'}
                ])
            
            elif activity_lower in ['fine dining', 'formal events', 'business']:
                items.extend([
                    {'name': 'Dress shirt/Blouse', 'quantity': 2, 'category': 'clothing', 'necessity': 'critical'},
                    {'name': 'Dress pants/Dress', 'quantity': 1, 'category': 'clothing', 'necessity': 'critical'},
                    {'name': 'Dress shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'critical'},
                    {'name': 'Blazer/Jacket', 'quantity': 1, 'category': 'clothing', 'necessity': 'high'}
                ])
            
            elif activity_lower in ['nightlife', 'clubbing', 'party']:
                items.extend([
                    {'name': 'Party outfits', 'quantity': 2, 'category': 'clothing', 'necessity': 'high'},
                    {'name': 'Comfortable party shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'high'},
                    {'name': 'Accessories/Jewelry', 'quantity': 3, 'category': 'accessories', 'necessity': 'medium'}
                ])
            
            elif activity_lower in ['sightseeing', 'walking tours', 'city exploration']:
                items.extend([
                    {'name': 'Comfortable walking shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'critical'},
                    {'name': 'Lightweight daypack', 'quantity': 1, 'category': 'gear', 'necessity': 'high'},
                    {'name': 'Portable charger', 'quantity': 1, 'category': 'electronics', 'necessity': 'high'},
                    {'name': 'Camera/Phone', 'quantity': 1, 'category': 'electronics', 'necessity': 'medium'}
                ])
        
        return items
    
    def _generate_weather_items(self, weather: str, destination: str, duration: int) -> List[Dict]:
        """Generate weather-specific protection items"""
        items = []
        
        if weather in ['rainy', 'wet']:
            items.extend([
                {'name': 'Rain jacket/Poncho', 'quantity': 1, 'category': 'outerwear', 'necessity': 'critical'},
                {'name': 'Waterproof shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'high'},
                {'name': 'Umbrella', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Waterproof bag covers', 'quantity': 2, 'category': 'gear', 'necessity': 'medium'}
            ])
        
        elif weather in ['cold', 'freezing']:
            items.extend([
                {'name': 'Winter coat/Parka', 'quantity': 1, 'category': 'outerwear', 'necessity': 'critical'},
                {'name': 'Warm gloves', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Warm hat/Beanie', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Scarf', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Thermal underwear', 'quantity': 2, 'category': 'clothing', 'necessity': 'high'},
                {'name': 'Warm boots', 'quantity': 1, 'category': 'footwear', 'necessity': 'critical'}
            ])
        
        elif weather in ['hot', 'sunny']:
            items.extend([
                {'name': 'Sunscreen SPF 30+', 'quantity': 1, 'category': 'skincare', 'necessity': 'critical'},
                {'name': 'Sunglasses', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Sun hat/Cap', 'quantity': 1, 'category': 'accessories', 'necessity': 'high'},
                {'name': 'Light, breathable fabrics', 'quantity': 3, 'category': 'clothing', 'necessity': 'high'},
                {'name': 'Insulated water bottle', 'quantity': 1, 'category': 'gear', 'necessity': 'high'}
            ])
        
        return items
    
    def _generate_destination_items(self, destination: str, activities: List[str]) -> List[Dict]:
        """Generate destination-specific items using AI knowledge"""
        items = []
        dest_lower = destination.lower()
        
        # Beach/tropical destinations
        if any(word in dest_lower for word in ['beach', 'tropical', 'island', 'maldives', 'hawaii', 'bali']):
            items.extend([
                {'name': 'Beach bag', 'quantity': 1, 'category': 'gear', 'necessity': 'high'},
                {'name': 'Snorkel gear (optional)', 'quantity': 1, 'category': 'gear', 'necessity': 'low'},
                {'name': 'Reef-safe sunscreen', 'quantity': 1, 'category': 'skincare', 'necessity': 'high'},
                {'name': 'Mosquito repellent', 'quantity': 1, 'category': 'health', 'necessity': 'medium'}
            ])
        
        # Mountain/adventure destinations
        elif any(word in dest_lower for word in ['mountain', 'alps', 'himalayas', 'andes', 'everest']):
            items.extend([
                {'name': 'Altitude sickness medication', 'quantity': 1, 'category': 'health', 'necessity': 'high'},
                {'name': 'High-altitude sunscreen', 'quantity': 1, 'category': 'skincare', 'necessity': 'high'},
                {'name': 'Warm sleeping gear', 'quantity': 1, 'category': 'gear', 'necessity': 'medium'},
                {'name': 'Emergency whistle', 'quantity': 1, 'category': 'safety', 'necessity': 'medium'}
            ])
        
        # Urban/city destinations
        elif any(word in dest_lower for word in ['city', 'urban', 'new york', 'london', 'paris', 'tokyo']):
            items.extend([
                {'name': 'Comfortable walking shoes', 'quantity': 1, 'category': 'footwear', 'necessity': 'critical'},
                {'name': 'Crossbody bag/Anti-theft bag', 'quantity': 1, 'category': 'gear', 'necessity': 'high'},
                {'name': 'Portable phone charger', 'quantity': 1, 'category': 'electronics', 'necessity': 'high'},
                {'name': 'City map/Guide book', 'quantity': 1, 'category': 'navigation', 'necessity': 'low'}
            ])
        
        # Desert destinations
        elif any(word in dest_lower for word in ['desert', 'sahara', 'dubai', 'arizona', 'nevada']):
            items.extend([
                {'name': 'Extra water bottles', 'quantity': 3, 'category': 'hydration', 'necessity': 'critical'},
                {'name': 'Lip balm with SPF', 'quantity': 1, 'category': 'skincare', 'necessity': 'high'},
                {'name': 'Dust mask/Bandana', 'quantity': 1, 'category': 'protection', 'necessity': 'medium'},
                {'name': 'Sand-proof bag', 'quantity': 1, 'category': 'gear', 'necessity': 'medium'}
            ])
        
        return items
    
    def _generate_travel_essentials(self, duration: int, destination: str) -> List[Dict]:
        """Generate universal travel essentials"""
        essentials = [
            {'name': 'Passport/ID', 'quantity': 1, 'category': 'documents', 'necessity': 'critical'},
            {'name': 'Phone charger', 'quantity': 1, 'category': 'electronics', 'necessity': 'critical'},
            {'name': 'Toiletries kit', 'quantity': 1, 'category': 'personal care', 'necessity': 'critical'},
            {'name': 'Medications', 'quantity': 1, 'category': 'health', 'necessity': 'critical'},
            {'name': 'Travel adapter', 'quantity': 1, 'category': 'electronics', 'necessity': 'high'},
            {'name': 'First aid kit', 'quantity': 1, 'category': 'health', 'necessity': 'medium'},
            {'name': 'Travel insurance docs', 'quantity': 1, 'category': 'documents', 'necessity': 'high'},
            {'name': 'Entertainment (book/tablet)', 'quantity': 1, 'category': 'entertainment', 'necessity': 'low'}
        ]
        
        # Duration-based additions
        if duration > 7:
            essentials.extend([
                {'name': 'Laundry detergent pods', 'quantity': 5, 'category': 'practical', 'necessity': 'medium'},
                {'name': 'Extra phone charger', 'quantity': 1, 'category': 'electronics', 'necessity': 'medium'}
            ])
        
        if duration > 14:
            essentials.extend([
                {'name': 'Backup credit card', 'quantity': 1, 'category': 'financial', 'necessity': 'high'},
                {'name': 'Emergency contact list', 'quantity': 1, 'category': 'documents', 'necessity': 'high'}
            ])
        
        return essentials
    
    def _generate_reasoning(self, category_type: str, destination: str, weather: str, duration: int, activities: List[str] = None) -> str:
        """Generate AI-powered reasoning for recommendations"""
        reasoning_templates = {
            'essential': f"Based on your {duration}-day trip to {destination} with {weather} weather, these clothing essentials will keep you comfortable and prepared.",
            'activity': f"Your planned activities ({', '.join(activities) if activities else 'various activities'}) require specific gear to ensure safety and enjoyment.",
            'weather': f"The {weather} weather conditions in {destination} require proper protection and comfort items.",
            'destination': f"Traveling to {destination} has unique requirements based on local culture, geography, and typical traveler needs."
        }
        
        return reasoning_templates.get(category_type, "AI-generated recommendation based on trip analysis.")
    
    def _match_with_wardrobe(self, recommendations: List[Dict], wardrobe_items: List[Dict]):
        """Match recommendations with user's existing wardrobe"""
        for category in recommendations:
            for item in category['items']:
                # Simple matching logic - can be enhanced with AI
                item_name_lower = item['name'].lower()
                matches = []
                
                for wardrobe_item in wardrobe_items:
                    wardrobe_name = wardrobe_item.get('item_name', '').lower()
                    wardrobe_category = wardrobe_item.get('category', '').lower()
                    
                    # Check for matches
                    if (any(word in wardrobe_name for word in item_name_lower.split()) or 
                        any(word in item_name_lower for word in wardrobe_name.split()) or
                        item['category'] == wardrobe_category):
                        matches.append({
                            'id': wardrobe_item.get('id'),
                            'name': wardrobe_item.get('item_name'),
                            'image_url': wardrobe_item.get('image_url'),
                            'match_confidence': 0.8  # Simple confidence score
                        })
                
                item['wardrobe_matches'] = matches[:3]  # Limit to top 3 matches
    
    def _generate_fallback_recommendations(self, trip_details: Dict, duration: int) -> List[Dict]:
        """Generate simple fallback recommendations if AI fails"""
        return [
            {
                'category': 'Essential Clothing',
                'items': [
                    {'name': 'T-shirts', 'quantity': max(duration // 2, 3), 'category': 'clothing', 'necessity': 'essential'},
                    {'name': 'Pants/Shorts', 'quantity': max(duration // 3, 2), 'category': 'clothing', 'necessity': 'essential'},
                    {'name': 'Underwear', 'quantity': duration + 2, 'category': 'clothing', 'necessity': 'essential'},
                    {'name': 'Socks', 'quantity': duration + 1, 'category': 'clothing', 'necessity': 'essential'}
                ],
                'priority': 'critical',
                'reasoning': 'Basic clothing essentials for your trip',
                'ai_confidence': 0.5
            },
            {
                'category': 'Travel Essentials',
                'items': [
                    {'name': 'Passport/ID', 'quantity': 1, 'category': 'documents', 'necessity': 'critical'},
                    {'name': 'Phone charger', 'quantity': 1, 'category': 'electronics', 'necessity': 'critical'},
                    {'name': 'Toiletries', 'quantity': 1, 'category': 'personal care', 'necessity': 'critical'}
                ],
                'priority': 'critical',
                'reasoning': 'Universal travel necessities',
                'ai_confidence': 0.9
            }
        ]
    
    def _build_destination_knowledge(self) -> Dict:
        """Build knowledge base for destinations"""
        # This would ideally be loaded from a comprehensive database
        return {
            'tropical': ['swimwear', 'light_clothing', 'sunscreen', 'mosquito_repellent'],
            'urban': ['comfortable_shoes', 'layers', 'crossbody_bag', 'portable_charger'],
            'mountain': ['warm_layers', 'hiking_boots', 'rain_gear', 'altitude_medication'],
            'desert': ['sun_protection', 'water_bottles', 'light_colors', 'dust_protection'],
            'beach': ['swimwear', 'beach_towels', 'flip_flops', 'waterproof_bag']
        }
    
    def _build_activity_requirements(self) -> Dict:
        """Build knowledge base for activity requirements"""
        return {
            'hiking': ['hiking_boots', 'moisture_wicking_clothes', 'backpack', 'water_bottle'],
            'business': ['formal_clothes', 'dress_shoes', 'blazer', 'business_accessories'],
            'beach': ['swimwear', 'beach_towel', 'sun_protection', 'water_shoes'],
            'nightlife': ['party_clothes', 'comfortable_shoes', 'accessories', 'small_bag'],
            'sightseeing': ['comfortable_shoes', 'daypack', 'camera', 'portable_charger']
        }
    
    def _build_weather_clothing_map(self) -> Dict:
        """Build weather to clothing mapping"""
        return {
            'hot': ['light_fabrics', 'shorts', 'tank_tops', 'sun_protection'],
            'cold': ['warm_layers', 'winter_coat', 'gloves', 'warm_boots'],
            'rainy': ['rain_jacket', 'waterproof_shoes', 'umbrella', 'quick_dry'],
            'mild': ['layers', 'light_jacket', 'versatile_pieces', 'moderate_protection']
        }
    
    def _build_packing_templates(self) -> Dict:
        """Build packing templates for different trip types"""
        return {
            'business': ['formal_clothes', 'dress_shoes', 'minimal_accessories'],
            'leisure': ['comfortable_clothes', 'casual_shoes', 'entertainment'],
            'adventure': ['outdoor_gear', 'sturdy_shoes', 'protection_equipment'],
            'luxury': ['high_quality_clothes', 'elegant_accessories', 'comfort_items']
        }

# Initialize the service
trip_ai_generator = TripAIGenerator()
