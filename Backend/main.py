from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import psycopg2
import os
import logging
import uvicorn
from dotenv import load_dotenv
from image_analysis import image_analysis_service
from services.analysis_history_service import analysis_history_service
from services.wardrobe_service import wardrobe_service
from services.image_storage_service import image_storage_service
from datetime import datetime
import json
import glob
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    # Startup
    try:
        # Test the image analysis service
        service_status = image_analysis_service.get_service_info()
        logger.info(f"Image analysis service initialized: {service_status}")
        
        # Test database connection
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            try:
                conn = psycopg2.connect(DATABASE_URL)
                conn.close()
                logger.info("Database connection successful")
            except Exception as e:
                logger.warning(f"Database connection failed: {e}")
        
        logger.info("Styra AI Backend started successfully!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Styra AI Backend shutting down...")

app = FastAPI(
    title="Styra AI Wardrobe Backend",
    description="Backend API with Free AI Clothing Analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files for images
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add to main.py

@app.post("/api/trip-planner/enhanced-packing")
async def enhanced_packing_recommendations(request_data: dict):
    """Generate enhanced packing recommendations with wardrobe integration"""
    try:
        trip_details = request_data.get('tripDetails', {})
        wardrobe_items = request_data.get('wardrobeItems', [])
        duration = request_data.get('duration', 7)
        
        # Analyze wardrobe for trip compatibility
        wardrobe_analysis = analyze_wardrobe_for_trip(wardrobe_items, trip_details)
        
        # Generate intelligent recommendations
        recommendations = generate_trip_recommendations(trip_details, wardrobe_analysis, duration)
        
        # Find specific wardrobe matches
        wardrobe_matches = find_wardrobe_matches(recommendations, wardrobe_items)
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "wardrobeMatches": wardrobe_matches,
            "analysis": wardrobe_analysis,
            "coverage": calculate_wardrobe_coverage(wardrobe_items, recommendations)
        }
        
    except Exception as e:
        logger.error(f"Enhanced packing recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate enhanced recommendations")

def analyze_wardrobe_for_trip(wardrobe_items, trip_details):
    """Analyze wardrobe compatibility with trip requirements"""
    
    activities = trip_details.get('activities', [])
    weather = trip_details.get('weatherExpected', '').lower()
    
    analysis = {
        'categories_coverage': {},
        'activity_readiness': {},
        'weather_preparedness': {},
        'gaps': []
    }
    
    # Categorize existing wardrobe
    categories = {}
    for item in wardrobe_items:
        category = item.get('category', 'unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Analyze category coverage
    essential_categories = ['tops', 'bottoms', 'shoes']
    for category in essential_categories:
        count = len(categories.get(category, []))
        analysis['categories_coverage'][category] = {
            'count': count,
            'adequacy': 'good' if count >= 3 else 'limited' if count >= 1 else 'missing'
        }
    
    # Activity readiness analysis
    activity_requirements = {
        'Business Meetings': ['business', 'formal'],
        'Beach/Pool': ['swimwear', 'casual'],
        'Hiking/Outdoor': ['athletic', 'outdoor'],
        'Fine Dining': ['formal', 'elegant'],
        'Nightlife': ['party', 'dressy']
    }
    
    for activity in activities:
        if activity in activity_requirements:
            required_styles = activity_requirements[activity]
            suitable_items = []
            
            for item in wardrobe_items:
                item_season = item.get('season', '').lower()
                if any(style in item_season for style in required_styles):
                    suitable_items.append(item)
            
            analysis['activity_readiness'][activity] = {
                'suitable_items': len(suitable_items),
                'readiness': 'ready' if len(suitable_items) >= 2 else 'partial' if len(suitable_items) >= 1 else 'unprepared'
            }
    
    # Weather preparedness
    if 'cold' in weather or 'winter' in weather:
        outerwear_count = len(categories.get('outerwear', []))
        analysis['weather_preparedness']['cold'] = {
            'outerwear_available': outerwear_count,
            'prepared': outerwear_count >= 1
        }
    
    if 'rain' in weather:
        # Look for rain-appropriate items
        rain_items = [item for item in wardrobe_items if 'rain' in item.get('name', '').lower()]
        analysis['weather_preparedness']['rain'] = {
            'rain_gear': len(rain_items),
            'prepared': len(rain_items) >= 1
        }
    
    # Identify gaps
    for category, info in analysis['categories_coverage'].items():
        if info['adequacy'] == 'missing':
            analysis['gaps'].append(f"No {category} in wardrobe")
        elif info['adequacy'] == 'limited':
            analysis['gaps'].append(f"Limited {category} options")
    
    return analysis

def generate_trip_recommendations(trip_details, wardrobe_analysis, duration):
    """Generate intelligent trip recommendations"""
    
    recommendations = {
        'must_pack': [],
        'consider_packing': [],
        'shopping_suggestions': [],
        'wardrobe_optimization': []
    }
    
    activities = trip_details.get('activities', [])
    weather = trip_details.get('weatherExpected', '').lower()
    packing_style = trip_details.get('packingStyle', 'comfort')
    
    # Base recommendations based on duration and style
    if packing_style == 'minimal':
        recommendations['must_pack'].extend([
            f"{max(3, duration // 2)} versatile tops",
            f"{max(2, duration // 3)} bottom pieces",
            "2 pairs of shoes maximum"
        ])
        recommendations['wardrobe_optimization'].append(
            "Focus on mix-and-match pieces that work for multiple occasions"
        )
    elif packing_style == 'fashion':
        recommendations['must_pack'].extend([
            f"{duration} different outfit options",
            "Statement accessories for outfit variety",
            "Multiple shoe options"
        ])
    
    # Activity-specific recommendations
    if 'Business Meetings' in activities:
        if wardrobe_analysis['activity_readiness'].get('Business Meetings', {}).get('readiness') != 'ready':
            recommendations['shopping_suggestions'].append("Professional business attire")
        recommendations['must_pack'].append("Business-appropriate shoes and accessories")
    
    if 'Beach/Pool' in activities:
        recommendations['must_pack'].extend(["Swimwear", "Sun protection accessories"])
        recommendations['consider_packing'].append("Beach cover-up")
    
    # Weather-specific recommendations
    if 'cold' in weather:
        if not wardrobe_analysis['weather_preparedness'].get('cold', {}).get('prepared'):
            recommendations['shopping_suggestions'].append("Warm outerwear")
        recommendations['must_pack'].extend(["Layering pieces", "Warm accessories"])
    
    if 'rain' in weather:
        if not wardrobe_analysis['weather_preparedness'].get('rain', {}).get('prepared'):
            recommendations['shopping_suggestions'].append("Rain jacket or umbrella")
    
    return recommendations

def find_wardrobe_matches(recommendations, wardrobe_items):
    """Find specific wardrobe items that match recommendations"""
    
    matches = {}
    
    for category, items in recommendations.items():
        matches[category] = []
        
        for recommendation in items:
            recommendation_lower = recommendation.lower()
            matching_items = []
            
            for item in wardrobe_items:
                item_name = item.get('name', '').lower()
                item_category = item.get('category', '').lower()
                
                # Simple keyword matching
                if any(keyword in item_name or keyword in item_category 
                      for keyword in recommendation_lower.split()):
                    matching_items.append({
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'category': item.get('category'),
                        'color': item.get('color'),
                        'image_url': item.get('image_url'),
                        'confidence': calculate_match_confidence(recommendation, item)
                    })
            
            # Sort by confidence and take top matches
            matching_items.sort(key=lambda x: x['confidence'], reverse=True)
            matches[category].append({
                'recommendation': recommendation,
                'matches': matching_items[:3]  # Top 3 matches
            })
    
    return matches

def calculate_match_confidence(recommendation, item):
    """Calculate how well a wardrobe item matches a recommendation"""
    
    rec_words = set(recommendation.lower().split())
    item_words = set((item.get('name', '') + ' ' + item.get('category', '')).lower().split())
    
    # Simple Jaccard similarity
    intersection = len(rec_words.intersection(item_words))
    union = len(rec_words.union(item_words))
    
    return intersection / union if union > 0 else 0

def calculate_wardrobe_coverage(wardrobe_items, recommendations):
    """Calculate how much of the trip needs can be covered by existing wardrobe"""
    
    total_recommendations = sum(len(items) for items in recommendations.values())
    
    if total_recommendations == 0:
        return {'percentage': 100, 'covered_count': 0, 'total_count': 0}
    
    covered_count = 0
    
    # Count recommendations that have wardrobe matches
    for category, items in recommendations.items():
        if category != 'shopping_suggestions':  # Don't count shopping suggestions as coverable
            for item in items:
                # Check if this recommendation has suitable wardrobe matches
                if has_suitable_wardrobe_match(item, wardrobe_items):
                    covered_count += 1
    
    coverage_percentage = (covered_count / total_recommendations) * 100
    
    return {
        'percentage': round(coverage_percentage, 1),
        'covered_count': covered_count,
        'total_count': total_recommendations,
        'status': 'excellent' if coverage_percentage >= 80 else 
                 'good' if coverage_percentage >= 60 else 
                 'moderate' if coverage_percentage >= 40 else 'low'
    }

def has_suitable_wardrobe_match(recommendation, wardrobe_items):
    """Check if a recommendation has a suitable match in the wardrobe"""
    
    rec_lower = recommendation.lower()
    
    for item in wardrobe_items:
        item_text = (item.get('name', '') + ' ' + item.get('category', '') + ' ' + 
                    item.get('color', '')).lower()
        
        # Check for keyword overlap
        rec_words = set(rec_lower.split())
        item_words = set(item_text.split())
        
        if len(rec_words.intersection(item_words)) >= 1:
            return True
    
    return False

@app.get("/api/trips")
async def get_user_trips(user_id: int = 1):
    """Get user's saved trips"""
    try:
        # TODO: Implement database query for user trips
        # For now, return mock data
        mock_trips = [
            {
                "id": "1",
                "destination": "Paris",
                "startDate": "2024-03-15",
                "endDate": "2024-03-22",
                "duration": 7,
                "activities": ["City Sightseeing", "Fine Dining", "Museums/Cultural"],
                "packingStyle": "fashion",
                "created_at": "2024-02-01"
            }
        ]
        
        return {
            "status": "success",
            "trips": mock_trips
        }
    except Exception as e:
        logger.error(f"Get trips error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trips")

@app.post("/api/trips")
async def save_trip(trip_data: dict):
    """Save trip details and packing list"""
    try:
        trip_id = str(uuid.uuid4())
        
        # TODO: Save to database
        # For now, just return success
        
        return {
            "status": "success",
            "trip_id": trip_id,
            "message": "Trip saved successfully"
        }
    except Exception as e:
        logger.error(f"Save trip error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save trip")
@app.get("/")
async def root():
    """Root endpoint with service information"""
    try:
        service_status = image_analysis_service.get_service_info()
        ai_status = "AI Models Loaded" if service_status.get('ai_models_loaded') else "Rule-based Analysis"
        
        return {
            "message": "Styra AI Wardrobe API",
            "status": "running",
            "version": "2.0.0",
            "database": "PostgreSQL",
            "ai_analysis": ai_status,
            "storage": "Static Files Only",
            "features": [
                "Free AI Clothing Analysis",
                "Automatic Category Detection",
                "Color Recognition",
                "Single Storage Method"
            ]
        }
    except Exception as e:
        return {
            "message": "Styra AI Wardrobe API",
            "status": "running",
            "version": "2.0.0",
            "ai_analysis": "Fallback Mode",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            health_status["services"]["database"] = {
                "status": "connected",
                "version": version[:50]
            }
        else:
            health_status["services"]["database"] = {
                "status": "not_configured",
                "message": "DATABASE_URL not set"
            }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check AI service
    try:
        ai_status = image_analysis_service.get_service_info()
        health_status["services"]["ai_analysis"] = {
            "status": "ready",
            "ai_models_loaded": ai_status.get('ai_models_loaded', False),
            "supported_categories": ai_status.get('supported_categories', []),
            "analysis_methods": ai_status.get('analysis_methods', [])
        }
    except Exception as e:
        health_status["services"]["ai_analysis"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

# Global variable to store the last analyzed image
last_analyzed_image = None

# Authentication Routes
@app.post("/auth/login")
async def login(credentials: dict):
    """User login endpoint"""
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": 1,
                "email": email,
                "name": "User"
            },
            "token": "mock_token_123"
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/signup")
async def signup(user_data: dict):
    """User signup endpoint"""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        name = user_data.get("name")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        return {
            "status": "success",
            "message": "Account created successfully",
            "user": {
                "id": 2,
                "email": email,
                "name": name or "New User"
            }
        }
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")

# Wardrobe Routes
@app.get("/api/wardrobe/items")
async def get_wardrobe_items(user_id: int = 1):
    """Get user's wardrobe items"""
    try:
        items = wardrobe_service.get_wardrobe_items()
        return {
            "status": "success",
            "items": items
        }
    except Exception as e:
        logger.error(f"Get wardrobe items error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve wardrobe items")

@app.post("/api/wardrobe/items")
async def add_wardrobe_item(item_data: dict):
    """Add item to wardrobe with smart image path detection"""
    global last_analyzed_image
    
    try:
        logger.info(f"Adding wardrobe item: {item_data.get('name', 'Unknown')}")
        logger.info(f"Item data keys: {list(item_data.keys())}")
        logger.info(f"Last analyzed image: {last_analyzed_image}")
        
        image_path = None
        
        # Strategy 1: Use the last analyzed image if this item comes from analysis
        if (last_analyzed_image and 
            item_data.get('analysisSource') == 'backend_ai' and 
            item_data.get('processed') == True):
            image_path = last_analyzed_image
            logger.info(f"Using last analyzed image: {image_path}")
        
        # Strategy 2: Look for explicit image URLs
        if not image_path:
            image_fields = ['image_url', 'image_path']
            for field in image_fields:
                if field in item_data and item_data[field] and item_data[field].startswith('/static/'):
                    image_path = item_data[field]
                    logger.info(f"Found explicit image path in {field}: {image_path}")
                    break
        
        # Strategy 3: Find the most recent analyzed image file
        if not image_path:
            try:
                images_dir = static_dir / "images" / "wardrobe"
                pattern = str(images_dir / "analyzed_item_*.jpg")
                image_files = glob.glob(pattern)
                
                if image_files:
                    # Get the most recent file
                    latest_file = max(image_files, key=os.path.getctime)
                    filename = os.path.basename(latest_file)
                    image_path = f"/static/images/wardrobe/{filename}"
                    logger.info(f"Found recent analyzed image: {image_path}")
            except Exception as e:
                logger.error(f"Error finding recent image: {e}")
        
        # Strategy 4: Try to save base64 data if present
        if not image_path:
            base64_fields = ['imageUri', 'image_data']
            for field in base64_fields:
                if field in item_data and item_data[field]:
                    image_value = item_data[field]
                    if isinstance(image_value, str) and ('data:image' in image_value or image_value.startswith('/9j/')):
                        try:
                            image_path = image_storage_service.save_image(image_value, "manual_add")
                            logger.info(f"Saved base64 image: {image_path}")
                            break
                        except Exception as img_error:
                            logger.error(f"Failed to save base64 image: {img_error}")
        
        # Clean up item data
        fields_to_remove = ['imageUri', 'image_data', 'imageData', 'image', 'image_url', 'captureDate', 'captureMetadata', 'processed', 'dateAdded', 'pendingSync']
        for field in fields_to_remove:
            item_data.pop(field, None)
        
        # Set the final image path
        item_data['image_path'] = image_path
        logger.info(f"Final image_path for database: {image_path}")
        
        # Map analysis fields to database fields
        if 'suggestedCategory' in item_data:
            item_data['category'] = item_data.pop('suggestedCategory')
        if 'suggestedColor' in item_data:
            item_data['color'] = item_data.pop('suggestedColor')
        if 'suggestedOccasion' in item_data:
            item_data['season'] = item_data.pop('suggestedOccasion')
        
        # Save item to database
        result = wardrobe_service.save_wardrobe_item(item_data)
        if result:
            logger.info(f"Wardrobe item saved with ID: {result['item_id']}")
            return {
                "status": "success",
                "message": "Item added to wardrobe",
                "item": {
                    "id": result["item_id"],
                    "created_at": result["created_at"].isoformat() if result["created_at"] else None,
                    "image_url": image_path,
                    **item_data
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save item to database")
            
    except Exception as e:
        logger.error(f"Add wardrobe item error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add item")

@app.delete("/api/wardrobe/items/{item_id}")
async def delete_wardrobe_item(item_id: int):
    """Delete a wardrobe item"""
    try:
        # Get the item first to clean up the image
        item = wardrobe_service.get_wardrobe_item_by_id(item_id)
        if item and item.get('image_path'):
            # Delete the image file
            image_storage_service.delete_image(item['image_path'])
        
        success = wardrobe_service.delete_wardrobe_item(item_id)
        if success:
            return {
                "status": "success",
                "message": "Item deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Delete wardrobe item error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")

# AI Analysis Routes
@app.post("/api/analyze-clothing")
async def analyze_clothing_image(image: UploadFile = File(...)):
    """Analyze clothing item and store image path globally"""
    global last_analyzed_image
    
    try:
        logger.info(f"Analyzing clothing image: {image.filename}")
        
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        image_data = await image.read()
        
        if len(image_data) > max_size:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Analyze the image using AI
        logger.info("Starting AI analysis...")
        analysis_result = image_analysis_service.analyze_clothing_item(image_data)
        logger.info(f"Analysis completed: {analysis_result.get('analysis_method')} - {analysis_result.get('confidence', 0):.2f}")
        
        # Save analysis result to database (for history tracking only)
        db_result = analysis_history_service.save_analysis_result(analysis_result)
        analysis_id = None
        if db_result:
            analysis_id = db_result['analysis_id']
            logger.info(f"Analysis saved to database with ID: {analysis_id}")
            analysis_result['analysis_id'] = analysis_id
        
        # Save image to static storage
        image_url = None
        if image_data:
            try:
                image_url = image_storage_service.save_image(image_data, "analyzed_item")
                logger.info(f"Image saved to static storage: {image_url}")
                
                # Store this as the last analyzed image
                last_analyzed_image = image_url
                analysis_result['image_url'] = image_url
                
            except Exception as e:
                logger.error(f"Static image storage failed: {e}")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "message": "Image analyzed successfully",
            "processing_info": {
                "file_size": len(image_data),
                "file_type": image.content_type,
                "analysis_time": analysis_result.get('processing_time', 0),
                "storage_method": "static_folder_only"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Backward compatibility routes
@app.get("/wardrobe/items")
async def get_wardrobe_items_compat(user_id: int = 1):
    return await get_wardrobe_items(user_id)

@app.post("/wardrobe/items")
async def add_wardrobe_item_compat(item_data: dict):
    return await add_wardrobe_item(item_data)

@app.get("/api/wardrobe/stats")
async def get_wardrobe_stats(user_id: int = 1):
    """Get wardrobe statistics"""
    try:
        items = wardrobe_service.get_wardrobe_items()
        total_items = len(items)
        
        # Calculate category distribution
        categories = {}
        colors = {}
        for item in items:
            cat = item.get('category', 'unknown')
            color = item.get('color', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
            colors[color] = colors.get(color, 0) + 1
        
        return {
            "status": "success",
            "stats": {
                "total_items": total_items,
                "categories": categories,
                "colors": colors,
                "most_worn_category": max(categories.keys(), key=categories.get) if categories else "none",
                "least_worn_category": min(categories.keys(), key=categories.get) if categories else "none",
                "ai_analysis_accuracy": 0.87
            }
        }
    except Exception as e:
        logger.error(f"Get wardrobe stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


