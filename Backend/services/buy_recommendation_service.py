# services/buy_recommendation_service.py
import json
from typing import Dict, List, Any
from datetime import datetime
from database.connection import db

class BuyRecommendationService:
    def __init__(self):
        pass
    
    def analyze_wardrobe(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's wardrobe to identify gaps and preferences"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all wardrobe items for the user with item names and details
                cursor.execute("""
                    SELECT id, name, category, color, season, created_at, times_worn
                    FROM wardrobe_items 
                    WHERE user_id = %s
                """, (user_id,))
                
                items = cursor.fetchall()
                
                print(f"Database query returned {len(items)} items")
                if len(items) > 0:
                    print(f"First item type: {type(items[0])}")
                    if hasattr(items[0], 'keys'):
                        print(f"First item keys: {list(items[0].keys())}")
                    else:
                        print(f"First item values: {items[0]}")
                
                if not items:
                    return {
                        "total_items": 0,
                        "categories": {},
                        "colors": {},
                        "specific_items": {},
                        "gaps": ["tops", "bottoms", "shoes", "outerwear"],
                        "style_preference": "unknown",
                        "recommendations": []
                    }
                
                # Analyze categories, colors, and specific items
                categories = {}
                colors = {}
                specific_items = {}  # Track specific item types like "denim jacket", "red trousers", etc.
                total_times_worn = 0
                
                print("Processing items...")
                for item in items:
                    # Determine how to access data based on item type
                    if hasattr(item, 'get'):  # If item is dict-like (RealDictCursor)
                        item_id = item.get('id')
                        item_name = item.get('name', '').lower() or "unknown"
                        category = item.get('category', '').lower() or "unknown"
                        color = item.get('color', '').lower() or "unknown"
                        times_worn = item.get('times_worn', 0) or 0
                    else:  # If item is tuple-like
                        item_id = item[0] if len(item) > 0 else None
                        item_name = str(item[1]).lower() if len(item) > 1 and item[1] else "unknown"
                        category = str(item[2]).lower() if len(item) > 2 and item[2] else "unknown"
                        color = str(item[3]).lower() if len(item) > 3 and item[3] else "unknown"
                        times_worn = item[6] if len(item) > 6 and item[6] is not None else 0
                    
                    print(f"Item {item_id}: name={item_name}, category={category}, color={color}, times_worn={times_worn}")
                    
                    # Process categories and colors
                    categories[category] = categories.get(category, 0) + 1
                    colors[color] = colors.get(color, 0) + 1
                    total_times_worn += times_worn
                    
                    # Process specific item types (like "denim jacket", "red trousers")
                    key_item_types = {
                        "denim jacket": ["denim jacket", "jean jacket", "jeans jacket"],
                        "blazer": ["blazer", "suit jacket", "formal jacket"],
                        "leather jacket": ["leather jacket", "leather coat"],
                        "red trousers": ["red trousers", "red pants", "burgundy trousers", "burgundy pants", "crimson pants"],
                        "white sneakers": ["white sneakers", "white shoes", "white trainers"],
                        "leather watch": ["watch", "leather watch", "wristwatch"],
                    }
                    
                    # Check if the item name contains any of the key item types
                    for item_type, keywords in key_item_types.items():
                        if any(keyword in item_name for keyword in keywords) or (
                            item_type == "red trousers" and "trousers" in item_name and "red" in color
                        ) or (
                            item_type == "white sneakers" and "sneakers" in item_name and "white" in color
                        ):
                            specific_items[item_type] = specific_items.get(item_type, 0) + 1
                            print(f"Found specific item: {item_type}")
                
                print(f"Categories after processing: {categories}")
                print(f"Colors after processing: {colors}")
                print(f"Specific items detected: {specific_items}")
                
                # Identify gaps
                essential_categories = ["tops", "bottoms", "shoes", "outerwear"]
                gaps = [cat for cat in essential_categories if categories.get(cat, 0) < 2]
                
                # Determine style preference based on categories
                style_preference = self._determine_style_preference(categories)
                
                return {
                    "total_items": len(items),
                    "categories": categories,
                    "colors": colors,
                    "specific_items": specific_items,
                    "gaps": gaps,
                    "style_preference": style_preference,
                    "most_common_color": max(colors, key=colors.get) if colors else "unknown",
                    "total_times_worn": total_times_worn
                }
            
        except Exception as e:
            print(f"Error analyzing wardrobe: {e}")
            return {
                "total_items": 0,
                "categories": {},
                "colors": {},
                "gaps": ["tops", "bottoms", "shoes", "outerwear"],
                "style_preference": "unknown",
                "recommendations": []
            }
    
    def _determine_style_preference(self, categories: Dict[str, int]) -> str:
        """Determine user's style preference based on their wardrobe"""
        total_items = sum(categories.values())
        
        if total_items == 0:
            return "unknown"
        
        # Calculate percentages
        casual_items = categories.get("t-shirts", 0) + categories.get("jeans", 0) + categories.get("sneakers", 0)
        formal_items = categories.get("shirts", 0) + categories.get("dress pants", 0) + categories.get("blazers", 0)
        
        casual_percentage = casual_items / total_items
        formal_percentage = formal_items / total_items
        
        if casual_percentage > 0.6:
            return "casual"
        elif formal_percentage > 0.4:
            return "formal"
        else:
            return "casual-professional"
    
    def generate_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate personalized buying recommendations"""
        try:
            analysis = self.analyze_wardrobe(user_id)
            recommendations = []
            
            categories = analysis.get("categories", {})
            gaps = analysis.get("gaps", [])
            colors = analysis.get("colors", {})
            specific_items = analysis.get("specific_items", {})
            style_preference = analysis.get("style_preference", "unknown")
            most_common_color = analysis.get("most_common_color", "unknown")
            
            # Generate recommendations based on gaps and avoid recommending items the user already has
            
            # 1. Denim jacket recommendation
            if ("outerwear" in gaps or categories.get("outerwear", 0) < 2) and specific_items.get("denim jacket", 0) == 0:
                recommendations.append({
                    "id": 1,
                    "item_type": "denim jacket",
                    "category": "outerwear",
                    "reason": f"You have {categories.get('tops', 0)} tops but lack versatile outerwear pieces. A denim jacket would complement your existing {style_preference} style.",
                    "priority": "high",
                    "estimated_price": "$45-80",
                    "color_suggestions": ["classic blue", "black", "white"],
                    "style_match": 85
                })
            # Alternative outerwear if user already has a denim jacket
            elif ("outerwear" in gaps or categories.get("outerwear", 0) < 2) and specific_items.get("leather jacket", 0) == 0:
                recommendations.append({
                    "id": 6,
                    "item_type": "leather jacket",
                    "category": "outerwear",
                    "reason": f"While you have a denim jacket, adding a leather jacket would give you more styling options and versatility for {style_preference} outfits.",
                    "priority": "medium",
                    "estimated_price": "$80-200",
                    "color_suggestions": ["black", "brown", "burgundy"],
                    "style_match": 82
                })
            
            # 2. Red trousers recommendation if user has tops but lacks matching bottoms
            if categories.get("tops", 0) > categories.get("bottoms", 0) and specific_items.get("red trousers", 0) == 0:
                if most_common_color in ["white", "black", "navy", "blue", "gray", "grey"]:
                    recommendations.append({
                        "id": 2,
                        "item_type": "red office trousers",
                        "category": "bottoms",
                        "reason": f"You have several {most_common_color} tops that would pair perfectly with red trousers for a professional yet stylish office look.",
                        "priority": "medium",
                        "estimated_price": "$35-60",
                        "color_suggestions": ["burgundy red", "deep red", "crimson"],
                        "style_match": 78
                    })
            
            # 3. White sneakers recommendation if missing shoes
            if ("shoes" in gaps or categories.get("shoes", 0) < 2) and specific_items.get("white sneakers", 0) == 0:
                recommendations.append({
                    "id": 3,
                    "item_type": "white sneakers",
                    "category": "shoes",
                    "reason": "Your wardrobe lacks casual footwear. White sneakers are versatile and would work with most of your casual outfits.",
                    "priority": "medium",
                    "estimated_price": "$50-120",
                    "color_suggestions": ["white", "off-white"],
                    "style_match": 82
                })
            
            # 4. Blazer recommendation for business casual looks
            if style_preference in ["casual-professional", "formal"] and specific_items.get("blazer", 0) == 0:
                recommendations.append({
                    "id": 4,
                    "item_type": "black blazer",
                    "category": "outerwear",
                    "reason": "A black blazer would instantly elevate your wardrobe and provide formal options for your existing pants and shirts.",
                    "priority": "high",
                    "estimated_price": "$60-150",
                    "color_suggestions": ["black", "navy blue"],
                    "style_match": 90
                })
            
            # 5. Watch recommendation for accessorizing
            if analysis.get("total_items", 0) > 10 and specific_items.get("leather watch", 0) == 0 and categories.get("accessories", 0) < 2:
                recommendations.append({
                    "id": 5,
                    "item_type": "leather watch",
                    "category": "accessories",
                    "reason": "Your wardrobe has good basics. A quality watch would add sophistication to both casual and formal outfits.",
                    "priority": "low",
                    "estimated_price": "$40-200",
                    "color_suggestions": ["brown leather", "black leather", "silver"],
                    "style_match": 75
                })
            
            # 6. Seasonal recommendations based on gaps
            current_month = datetime.now().month
            if 5 <= current_month <= 8:  # Summer months
                if "bottoms" in gaps and "shorts" not in specific_items:
                    recommendations.append({
                        "id": 7,
                        "item_type": "chino shorts",
                        "category": "bottoms",
                        "reason": "Summer is here! Add versatile chino shorts to stay cool while maintaining style.",
                        "priority": "medium",
                        "estimated_price": "$30-50",
                        "color_suggestions": ["beige", "navy", "olive"],
                        "style_match": 85
                    })
            elif 11 <= current_month <= 12 or 1 <= current_month <= 2:  # Winter months
                if "outerwear" in gaps and specific_items.get("winter coat", 0) == 0:
                    recommendations.append({
                        "id": 8,
                        "item_type": "winter coat",
                        "category": "outerwear",
                        "reason": "Winter is coming! A proper winter coat will keep you warm and stylish during the colder months.",
                        "priority": "high",
                        "estimated_price": "$80-200",
                        "color_suggestions": ["black", "navy", "camel"],
                        "style_match": 88
                    })
                    
            # 7. Versatile dress shirt if user's wardrobe is casual-heavy
            if style_preference == "casual" and categories.get("shirts", 0) < 2:
                recommendations.append({
                    "id": 9,
                    "item_type": "oxford dress shirt",
                    "category": "tops",
                    "reason": "Your wardrobe is primarily casual. Adding a classic oxford shirt would give you options for more formal occasions.",
                    "priority": "medium", 
                    "estimated_price": "$35-70",
                    "color_suggestions": ["light blue", "white", "pink"],
                    "style_match": 80
                })
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def get_recommendations_with_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get complete recommendations with analytics"""
        try:
            analysis = self.analyze_wardrobe(user_id)
            recommendations = self.generate_recommendations(user_id)
            
            # Calculate budget recommendation
            total_items = analysis.get("total_items", 0)
            if total_items < 5:
                budget_range = "$150-300 for wardrobe basics"
                budget_priority = "high"
            elif total_items < 15:
                budget_range = "$200-400 for wardrobe completion"
                budget_priority = "medium"
            else:
                budget_range = "$100-200 for style enhancement"
                budget_priority = "low"
            
            # Determine wardrobe completeness
            categories = analysis.get("categories", {})
            specific_items = analysis.get("specific_items", {})
            gaps = analysis.get("gaps", [])
            
            # Calculate wardrobe versatility score
            essential_categories = ["tops", "bottoms", "shoes", "outerwear"]
            category_coverage = sum(1 for cat in essential_categories if categories.get(cat, 0) >= 2)
            versatility_score = min(100, (category_coverage / len(essential_categories)) * 100)
            
            # Determine wardrobe focus areas
            focus_areas = []
            if categories.get("tops", 0) < 3:
                focus_areas.append("tops")
            if categories.get("bottoms", 0) < 2:
                focus_areas.append("bottoms")
            if categories.get("shoes", 0) < 2:
                focus_areas.append("shoes")
            if categories.get("outerwear", 0) < 2:
                focus_areas.append("outerwear")
            if total_items > 15 and categories.get("accessories", 0) < 2:
                focus_areas.append("accessories")
            
            # Add seasonal recommendations
            current_month = datetime.now().month
            if 5 <= current_month <= 8:  # Summer
                if "summer" not in [season.lower() for item, count in categories.items() for season in ['summer']]:
                    focus_areas.append("summer wear")
            elif 11 <= current_month <= 2:  # Winter
                if "winter" not in [season.lower() for item, count in categories.items() for season in ['winter']]:
                    focus_areas.append("winter wear")
            
            return {
                "status": "success",
                "recommendations": recommendations,
                "analytics": {
                    "wardrobe_gaps": gaps,
                    "style_preference": analysis.get("style_preference", "unknown"),
                    "most_needed": "versatile pieces" if len(gaps) > 2 else "style enhancement",
                    "budget_recommendation": budget_range,
                    "budget_priority": budget_priority,
                    "total_wardrobe_items": total_items,
                    "versatility_score": int(versatility_score),
                    "focus_areas": focus_areas,
                    "color_palette": {
                        "dominant": analysis.get("most_common_color", "unknown"),
                        "suggested_accents": self._get_complementary_colors(analysis.get("most_common_color", "unknown"))
                    },
                    "wardrobe_statistics": {
                        "categories": categories,
                        "specific_items": specific_items
                    }
                }
            }
            
        except Exception as e:
            print(f"Error getting recommendations with analytics: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate recommendations: {str(e)}",
                "recommendations": [],
                "analytics": {}
            }
    
    def _get_complementary_colors(self, base_color: str) -> List[str]:
        """Get complementary colors for a base color"""
        color_combinations = {
            "black": ["white", "red", "gray", "yellow"],
            "white": ["black", "navy", "red", "blue"],
            "blue": ["orange", "yellow", "white", "pink"],
            "navy": ["white", "beige", "pink", "light blue"],
            "red": ["white", "black", "gray", "navy"],
            "green": ["pink", "beige", "white", "brown"],
            "yellow": ["navy", "black", "purple", "gray"],
            "purple": ["yellow", "white", "gray", "beige"],
            "pink": ["navy", "gray", "green", "black"],
            "gray": ["pink", "navy", "red", "black"],
            "beige": ["navy", "brown", "black", "green"],
            "brown": ["blue", "light blue", "white", "beige"]
        }
        
        return color_combinations.get(base_color.lower(), ["white", "black", "blue", "beige"])
