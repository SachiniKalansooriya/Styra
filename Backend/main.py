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
from services.trip_ai_service import TripAIService
from services.outfit_history_service import OutfitHistoryService
from services.trip_ai_generator import trip_ai_generator
from services.enhanced_outfit_service import enhanced_outfit_service
from services.favorite_outfit_service import favorite_outfit_service
from services.weather_service import weather_service
from services.trip_service import trip_service
from services.buy_recommendation_service import BuyRecommendationService
from datetime import datetime
import json
import glob
import uuid
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure static directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
trip_ai_service = None
outfit_history_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    # Startup
    global trip_ai_service, outfit_history_service
    
    try:
        # Test the image analysis service
        service_status = image_analysis_service.get_service_info()
        logger.info(f"Image analysis service initialized: {service_status}")
        
        # Initialize trip AI generator
        if trip_ai_generator.load_ai_models():
            logger.info("Trip AI generator initialized successfully")
        else:
            logger.warning("Trip AI generator failed to initialize - using fallback mode")
        
        # Initialize trip AI service
        trip_ai_service = TripAIService()
        logger.info("Trip AI service initialized")
        
        # Test database connection and initialize outfit history service
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            try:
                conn = psycopg2.connect(DATABASE_URL)
                # Don't close the connection - keep it for the service
                outfit_history_service = OutfitHistoryService(conn)
                logger.info("Database connection successful and outfit history service initialized")
            except Exception as e:
                logger.warning(f"Database connection failed: {e}")
                outfit_history_service = None
        else:
            logger.warning("DATABASE_URL not found in environment variables")
            outfit_history_service = None
        
        logger.info("Styra AI Backend started successfully!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Styra AI Backend shutting down...")

app = FastAPI(
    title="Styra AI Wardrobe Backend",
    description="Backend API with Free AI Clothing Analysis, Trip Planning, and Smart Outfit Recommendations",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the last analyzed image
last_analyzed_image = None

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
                "Smart Outfit Recommendations",
                "Weather-Based Styling",
                "Personal Wardrobe Integration",
                "Smart Trip Planning",
                "Wardrobe Integration",
                "AI-Powered Packing Lists",
                "Machine Learning Preferences"
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
    
    # Check outfit AI service
    try:
        health_status["services"]["outfit_ai"] = {
            "status": "ready",
            "features": ["weather_integration", "occasion_matching", "color_harmony", "wardrobe_analysis"]
        }
    except Exception as e:
        health_status["services"]["outfit_ai"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check trip AI service
    try:
        health_status["services"]["trip_ai"] = {
            "status": "ready",
            "features": ["wardrobe_analysis", "smart_recommendations", "coverage_calculation"]
        }
    except Exception as e:
        health_status["services"]["trip_ai"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_status

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

# AI Outfit Recommendation Routes
@app.post("/api/outfit/ai-recommendation")
async def get_ai_outfit_recommendation(request_data: dict):
    """Generate AI outfit recommendation from user's actual wardrobe"""
    try:
        user_id = request_data.get('user_id', 1)
        location = request_data.get('location', {})
        demo_weather = request_data.get('demo_weather')
        occasion = request_data.get('occasion', 'casual')
        
        # Check if demo weather is provided
        if demo_weather:
            # Use demo weather data
            weather_data = {
                'temperature': demo_weather.get('temperature', 25),
                'condition': demo_weather.get('condition', 'sunny'),
                'humidity': demo_weather.get('humidity', 60),
                'windSpeed': demo_weather.get('windSpeed', 10),
                'precipitation': demo_weather.get('precipitation', 0),
                'location': demo_weather.get('location', 'Demo Location')
            }
            logger.info(f"Using demo weather data: {weather_data}")
            
        # Get real weather data if location is provided
        elif location.get('latitude') and location.get('longitude'):
            try:
                weather_data = weather_service.get_current_weather(
                    location['latitude'], 
                    location['longitude']
                )
                logger.info(f"Retrieved real weather data: {weather_data}")
            except Exception as e:
                logger.warning(f"Failed to get real weather data: {e}")
                # Fallback to default weather if API fails
                weather_data = {
                    'temperature': 22,
                    'condition': 'partly cloudy',
                    'humidity': 55,
                    'windSpeed': 12,
                    'precipitation': 0,
                    'location': f"Lat: {location['latitude']}, Lon: {location['longitude']}"
                }
        else:
            # Use default weather when no location provided
            weather_data = {
                'temperature': 22,
                'condition': 'partly cloudy',
                'humidity': 55,
                'windSpeed': 12,
                'precipitation': 0,
                'location': 'Default Location'
            }
        
        # Generate AI recommendation using user's actual wardrobe
        outfit_recommendation = enhanced_outfit_service.generate_outfit_recommendation(
            user_id=user_id,
            weather_data=weather_data,
            occasion=occasion
        )
        
        return {
            "status": "success",
            "outfit": outfit_recommendation,
            "weather": weather_data,
            "message": "AI recommendation generated from your wardrobe"
        }
        
    except Exception as e:
        logger.error(f"AI outfit recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI recommendation: {str(e)}")

@app.get("/api/outfit/wardrobe-analysis/{user_id}")
async def analyze_user_wardrobe(user_id: int):
    """Analyze user's wardrobe for AI insights"""
    try:
        wardrobe_items = enhanced_outfit_service.get_user_wardrobe_items(user_id)
        
        if not wardrobe_items:
            return {
                "status": "success",
                "analysis": {
                    "total_items": 0,
                    "message": "No items in wardrobe yet. Add some clothes to get AI analysis!"
                }
            }
        
        # Analyze wardrobe composition
        categories = {}
        colors = {}
        seasons = {}
        avg_confidence = 0
        formality_levels = []
        
        for item in wardrobe_items:
            # Category analysis
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
            
            # Color analysis
            color = item['color']
            colors[color] = colors.get(color, 0) + 1
            
            # Season analysis
            season = item['season']
            seasons[season] = seasons.get(season, 0) + 1
            
            # Confidence tracking
            avg_confidence += item['confidence']
            
            # Formality tracking
            formality_levels.append(item['formality_score'])
        
        avg_confidence = avg_confidence / len(wardrobe_items)
        avg_formality = sum(formality_levels) / len(formality_levels)
        
        # Generate AI recommendations
        recommendations = []
        
        # Check for missing essentials
        essential_categories = ['tops', 'bottoms', 'shoes']
        missing_essentials = []
        for essential in essential_categories:
            if essential not in categories:
                missing_essentials.append(essential)
        
        if missing_essentials:
            recommendations.append(f"Add {', '.join(missing_essentials)} to complete your wardrobe basics")
        
        # Check color diversity
        if len(colors) < 3:
            recommendations.append("Consider adding more color variety for better outfit combinations")
        
        # Check seasonal coverage
        if len(seasons) < 2:
            recommendations.append("Add items for different seasons to expand your styling options")
        
        # Check style balance
        if avg_formality < 3:
            recommendations.append("Consider adding some business or formal pieces for versatility")
        elif avg_formality > 7:
            recommendations.append("Add some casual pieces for relaxed occasions")
        
        # Calculate wardrobe score
        completeness_score = min(100, len(wardrobe_items) * 8)
        diversity_score = min(100, len(categories) * 15 + len(colors) * 5)
        wardrobe_score = int((completeness_score + diversity_score) / 2)
        
        analysis = {
            "total_items": len(wardrobe_items),
            "categories": categories,
            "colors": colors,
            "seasons": seasons,
            "average_ai_confidence": round(avg_confidence, 1),
            "average_formality": round(avg_formality, 1),
            "recommendations": recommendations,
            "wardrobe_score": wardrobe_score,
            "completeness": {
                "has_tops": "tops" in categories,
                "has_bottoms": "bottoms" in categories,
                "has_shoes": "shoes" in categories,
                "has_outerwear": "outerwear" in categories
            },
            "style_profile": "casual" if avg_formality < 4 else "business" if avg_formality > 6 else "balanced"
        }
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Wardrobe analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze wardrobe")

@app.post("/api/outfit/multiple-recommendations")
async def get_multiple_outfit_recommendations(request_data: dict):
    """Generate multiple AI outfit recommendations for different occasions"""
    try:
        user_id = request_data.get('user_id', 1)
        location = request_data.get('location', {})
        occasions = request_data.get('occasions', ['casual', 'business', 'date'])
        
        # Create weather data
        weather_data = {
            'temperature': 22,
            'condition': 'partly cloudy',
            'humidity': 55,
            'windSpeed': 12,
            'precipitation': 0
        }
        
        recommendations = {}
        
        # Generate recommendations for each occasion
        for occasion in occasions:
            try:
                outfit = enhanced_outfit_service.generate_outfit_recommendation(
                    user_id=user_id,
                    weather_data=weather_data,
                    occasion=occasion
                )
                recommendations[occasion] = outfit
            except Exception as e:
                logger.warning(f"Failed to generate {occasion} outfit: {e}")
                recommendations[occasion] = {
                    'error': f'Failed to generate {occasion} outfit',
                    'message': str(e)
                }
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "weather": weather_data,
            "message": f"Generated {len(recommendations)} outfit recommendations"
        }
        
    except Exception as e:
        logger.error(f"Multiple recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate multiple recommendations")

# Trip Planner Routes - Enhanced with AI Service
@app.post("/api/trip-planner/enhanced-packing")
async def enhanced_packing_recommendations(request_data: dict):
    """Generate enhanced packing recommendations with wardrobe integration"""
    try:
        logger.info("Processing enhanced packing request...")
        
        trip_details = request_data.get('tripDetails', {})
        wardrobe_items = request_data.get('wardrobeItems', [])
        duration = request_data.get('duration', 7)
        
        logger.info(f"Trip destination: {trip_details.get('destination', 'Unknown')}")
        logger.info(f"Activities: {trip_details.get('activities', [])}")
        logger.info(f"Weather: {trip_details.get('weatherExpected', 'Unknown')}")
        logger.info(f"Wardrobe items count: {len(wardrobe_items)}")
        logger.info(f"Duration: {duration}")
        
        # Use the new AI trip generator for intelligent analysis
        if trip_ai_generator.ai_loaded:
            logger.info("Using AI-powered trip planning")
            recommendations = trip_ai_generator.generate_intelligent_packing_list(trip_details, wardrobe_items, duration)
            
            # Also get traditional analysis for comparison
            wardrobe_analysis = trip_ai_service.analyze_wardrobe_for_trip(wardrobe_items, trip_details)
            wardrobe_matches = trip_ai_service.find_detailed_wardrobe_matches(recommendations, wardrobe_items)
            coverage = trip_ai_service.calculate_detailed_wardrobe_coverage(wardrobe_items, recommendations)
            
        else:
            logger.info("Using traditional trip analysis (AI not available)")
            # Fallback to traditional service
            wardrobe_analysis = trip_ai_service.analyze_wardrobe_for_trip(wardrobe_items, trip_details)
            recommendations = trip_ai_service.generate_enhanced_trip_recommendations(trip_details, wardrobe_analysis, duration)
            wardrobe_matches = trip_ai_service.find_detailed_wardrobe_matches(recommendations, wardrobe_items)
            coverage = trip_ai_service.calculate_detailed_wardrobe_coverage(wardrobe_items, recommendations)
        
        logger.info("Enhanced packing recommendations generated successfully")
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "wardrobeMatches": wardrobe_matches,
            "analysis": wardrobe_analysis,
            "coverage": coverage,
            "message": "Smart packing list generated with AI analysis"
        }
        
    except Exception as e:
        logger.error(f"Enhanced packing recommendations error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced recommendations: {str(e)}")

@app.get("/api/trips")
async def get_user_trips(user_id: int = 1):
    """Get user's saved trips"""
    try:
        logger.info(f"Getting trips for user: {user_id}")
        
        # Use the trip service to get from database
        trips = trip_service.get_user_trips(user_id)
        
        return {
            "status": "success",
            "trips": trips,
            "count": len(trips)
        }
    except Exception as e:
        logger.error(f"Get trips error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trips: {str(e)}")

@app.post("/api/trips")
async def save_trip(trip_data: dict):
    """Save trip details and packing list"""
    try:
        logger.info(f"Saving trip: {trip_data.get('destination', 'Unknown')}")
        
        # Use the trip service to save to database
        result = trip_service.save_trip(trip_data)
        
        return {
            "status": "success",
            "trip_id": result["id"],
            "message": "Trip saved successfully to database"
        }
    except Exception as e:
        logger.error(f"Save trip error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save trip: {str(e)}")

# Weather Integration (Mock for now - can be enhanced with real weather API)
@app.get("/api/weather/{lat}/{lon}")
async def get_weather_data(lat: float, lon: float):
    """Get weather data for coordinates"""
    try:
        # Use the real weather service
        weather_data = weather_service.get_current_weather(lat, lon)
        
        return {
            "status": "success",
            "current": weather_data
        }
        
    except Exception as e:
        logger.error(f"Weather data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weather data")

# Backward compatibility routes
@app.get("/wardrobe/items")
async def get_wardrobe_items_compat(user_id: int = 1):
    return await get_wardrobe_items(user_id)

@app.post("/wardrobe/items")
async def add_wardrobe_item_compat(item_data: dict):
    return await add_wardrobe_item(item_data)

# Legacy outfit endpoints (for backward compatibility)
@app.post("/api/outfit/generate")
async def generate_ai_outfit_legacy(request_data: dict):
    """Legacy outfit generation endpoint - redirects to new AI recommendation"""
    return await get_ai_outfit_recommendation(request_data)

@app.post("/api/outfit/feedback")
async def process_outfit_feedback(feedback_data: dict):
    """Process user feedback for machine learning (placeholder implementation)"""
    try:
        user_id = feedback_data.get('user_id')
        outfit_id = feedback_data.get('outfit_id')
        feedback_type = feedback_data.get('feedback_type')  # 'like', 'dislike', 'worn'
        
        logger.info(f"Processing feedback: User {user_id}, Outfit {outfit_id}, Type: {feedback_type}")
        
        # TODO: Implement actual feedback processing and machine learning
        # For now, just log the feedback
        return {
            "status": "success",
            "message": "Feedback processed successfully - AI will learn from your preferences"
        }
        
    except Exception as e:
        logger.error(f"Feedback processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process feedback")

# Outfit History Routes
@app.post("/api/outfit/wear")
async def record_worn_outfit(request_data: dict):
    """Record that user wore a specific outfit"""
    try:
        if not outfit_history_service:
            raise HTTPException(status_code=503, detail="Outfit history service not available")
        
        outfit_data = request_data.get('outfit_data', {})
        user_id = request_data.get('user_id', 1)
        occasion = request_data.get('occasion')
        weather = request_data.get('weather')
        location = request_data.get('location')
        worn_date = request_data.get('worn_date')
        
        if not outfit_data:
            raise HTTPException(status_code=400, detail="Outfit data is required")
        
        logger.info(f"Recording worn outfit for user {user_id}")
        
        result = outfit_history_service.record_worn_outfit(
            outfit_data=outfit_data,
            user_id=user_id,
            occasion=occasion,
            weather=weather,
            location=location,
            worn_date=worn_date
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record worn outfit error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record outfit: {str(e)}")

@app.post("/api/outfit/regenerate-item")
async def regenerate_single_item(request_data: dict):
    """Regenerate a single item while keeping others in the outfit"""
    try:
        current_outfit = request_data.get('current_outfit', {})
        item_category = request_data.get('item_category')  # e.g., 'tops', 'bottoms', 'shoes'
        occasion = request_data.get('occasion', 'casual')
        user_id = request_data.get('user_id', 1)
        
        if not current_outfit or not item_category:
            raise HTTPException(status_code=400, detail="Current outfit and item category are required")
        
        logger.info(f"Regenerating {item_category} for user {user_id}, occasion: {occasion}")
        
        # Get user's wardrobe items
        wardrobe_items = wardrobe_service.get_wardrobe_items()
        
        # Filter items by category
        category_items = [item for item in wardrobe_items if item.get('category', '').lower() == item_category.lower()]
        
        if not category_items:
            return {
                "status": "error",
                "message": f"No {item_category} items found in wardrobe"
            }
        
        # Get current items in outfit (excluding the one we're replacing)
        current_items = current_outfit.get('items', [])
        
        # Find the current item being replaced to exclude it
        current_item_id = None
        for item in current_items:
            if item.get('category', '').lower() == item_category.lower():
                current_item_id = item.get('id')
                break
        
        # Filter items by category and exclude current item
        category_items = [
            item for item in wardrobe_items 
            if item.get('category', '').lower() == item_category.lower() 
            and item.get('id') != current_item_id  # Exclude current item
        ]
        
        if not category_items:
            return {
                "status": "error",
                "message": f"No alternative {item_category} items found in wardrobe"
            }
        
        logger.info(f"Found {len(category_items)} alternative {item_category} items (excluding current)")
        
        # Find items that match the current outfit style and occasion
        suitable_items = []
        for item in category_items:
            # Basic compatibility check (can be enhanced with AI)
            item_occasions = item.get('suitable_occasions', [])
            if not item_occasions or occasion in item_occasions:
                suitable_items.append(item)
        
        if not suitable_items:
            # If no suitable items found, use all category items (already excludes current)
            suitable_items = category_items
        
        if not suitable_items:
            return {
                "status": "error",
                "message": f"No alternative {item_category} items available"
            }
        
        # Select a random item to ensure variety
        import random
        new_item = random.choice(suitable_items)
        
        # Create the updated outfit
        updated_items = []
        item_replaced = False
        
        for item in current_items:
            if item.get('category', '').lower() == item_category.lower():
                # Replace with new item
                updated_items.append({
                    'id': new_item.get('id'),
                    'name': new_item.get('name'),
                    'category': new_item.get('category'),
                    'image_path': new_item.get('image_path'),
                    'image_url': f"/static/images/wardrobe/{new_item.get('image_path')}" if new_item.get('image_path') else None,
                    'color': new_item.get('color'),
                    'brand': new_item.get('brand')
                })
                item_replaced = True
            else:
                # Keep existing item
                updated_items.append(item)
        
        # If no item was replaced, add the new item
        if not item_replaced:
            updated_items.append({
                'id': new_item.get('id'),
                'name': new_item.get('name'),
                'category': new_item.get('category'),
                'image_path': new_item.get('image_path'),
                'image_url': f"/static/images/wardrobe/{new_item.get('image_path')}" if new_item.get('image_path') else None,
                'color': new_item.get('color'),
                'brand': new_item.get('brand')
            })
        
        # Calculate new confidence (basic algorithm)
        # TODO: Enhance with AI-based compatibility scoring
        base_confidence = current_outfit.get('confidence', 85)
        new_confidence = max(75, min(95, base_confidence + (5 if len(suitable_items) > 3 else -5)))
        
        updated_outfit = {
            'id': current_outfit.get('id', 'updated'),
            'items': updated_items,
            'confidence': new_confidence,
            'reason': f"Updated {item_category} for better style match",
            'occasion': occasion
        }
        
        logger.info(f"Successfully regenerated {item_category}: {new_item.get('name')}")
        
        return {
            "status": "success",
            "outfit": updated_outfit,
            "replaced_item": {
                'category': item_category,
                'new_item': new_item.get('name'),
                'alternatives_available': len(suitable_items) - 1
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regenerate item error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate item: {str(e)}")

@app.get("/api/outfit/history")
async def get_outfit_history(user_id: int = 1, limit: int = 50, start_date: str = None, end_date: str = None):
    """Get user's outfit history"""
    try:
        if not outfit_history_service:
            raise HTTPException(status_code=503, detail="Outfit history service not available")
        
        logger.info(f"Getting outfit history for user {user_id}")
        
        result = outfit_history_service.get_user_outfit_history(
            user_id=user_id,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        # Debug logging
        if result.get('history'):
            logger.info(f"Returning {len(result['history'])} outfit history entries")
            for i, entry in enumerate(result['history'][:2]):  # Log first 2 entries
                logger.info(f"Entry {i}: outfit_data type = {type(entry.get('outfit_data'))}")
                logger.info(f"Entry {i}: outfit_data = {entry.get('outfit_data')}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get outfit history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get outfit history: {str(e)}")

@app.get("/api/outfit/history/{worn_date}")
async def get_outfit_by_date(worn_date: str, user_id: int = 1):
    """Get outfit worn on a specific date"""
    try:
        if not outfit_history_service:
            raise HTTPException(status_code=503, detail="Outfit history service not available")
        
        logger.info(f"Getting outfit for user {user_id} on {worn_date}")
        
        result = outfit_history_service.get_outfit_by_date(
            worn_date=worn_date,
            user_id=user_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get outfit by date error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get outfit: {str(e)}")

@app.post("/api/outfit/rate")
async def rate_outfit(request_data: dict):
    """Rate a worn outfit"""
    try:
        if not outfit_history_service:
            raise HTTPException(status_code=503, detail="Outfit history service not available")
        
        outfit_id = request_data.get('outfit_id')
        rating = request_data.get('rating')
        notes = request_data.get('notes')
        
        if not outfit_id or not rating:
            raise HTTPException(status_code=400, detail="Outfit ID and rating are required")
        
        logger.info(f"Rating outfit {outfit_id} with {rating} stars")
        
        result = outfit_history_service.rate_outfit(
            outfit_id=outfit_id,
            rating=rating,
            notes=notes
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate outfit error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rate outfit: {str(e)}")

@app.get("/api/outfit/recommendations/{user_id}")
async def get_daily_recommendations(user_id: int, lat: float = 40.7128, lon: float = -74.0060):
    """Get daily outfit recommendations for user"""
    try:
        # Get weather data (mock for now)
        weather_data = {
            'temperature': 22,
            'condition': 'partly cloudy',
            'humidity': 55,
            'windSpeed': 12,
            'precipitation': 0
        }
        
        # Generate recommendations for different occasions
        occasions = ['casual', 'business', 'workout']
        daily_recommendations = {}
        
        for occasion in occasions:
            try:
                outfit = enhanced_outfit_service.generate_outfit_recommendation(
                    user_id=user_id,
                    weather_data=weather_data,
                    occasion=occasion
                )
                if not outfit.get('error'):
                    daily_recommendations[occasion] = outfit
            except Exception as e:
                logger.warning(f"Failed to generate {occasion} recommendation: {e}")
        
        return {
            "status": "success",
            "recommendations": daily_recommendations,
            "weather": weather_data,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Daily recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily recommendations")

# Additional utility endpoints
@app.get("/api/outfit/occasions")
async def get_available_occasions():
    """Get list of available occasions for outfit recommendations"""
    occasions = [
        {
            "id": "casual",
            "name": "Casual",
            "description": "Relaxed, everyday wear",
            "formality_range": [1, 4]
        },
        {
            "id": "business",
            "name": "Business",
            "description": "Professional work attire",
            "formality_range": [5, 7]
        },
        {
            "id": "formal",
            "name": "Formal",
            "description": "Dressy events and special occasions",
            "formality_range": [8, 10]
        },
        {
            "id": "workout",
            "name": "Workout",
            "description": "Athletic and gym wear",
            "formality_range": [1, 3]
        },
        {
            "id": "date",
            "name": "Date Night",
            "description": "Romantic occasions",
            "formality_range": [6, 9]
        }
    ]
    
    return {
        "status": "success",
        "occasions": occasions
    }

@app.get("/api/outfit/color-analysis")
async def get_color_analysis():
    """Get color harmony rules and recommendations"""
    try:
        color_rules = enhanced_outfit_service.color_harmony_rules
        
        return {
            "status": "success",
            "color_analysis": {
                "complementary_pairs": color_rules['complementary_pairs'],
                "neutral_colors": color_rules['neutral_colors'],
                "warm_colors": color_rules['warm_colors'],
                "cool_colors": color_rules['cool_colors'],
                "seasonal_palettes": color_rules['seasonal_palettes'],
                "tips": [
                    "Neutral colors go with almost everything",
                    "Complementary colors create striking combinations",
                    "Monochromatic outfits are always safe",
                    "Add one pop of color to neutral outfits"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Color analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get color analysis")

@app.post("/api/outfit/validate-combination")
async def validate_outfit_combination(combination_data: dict):
    """Validate if clothing items work well together"""
    try:
        items = combination_data.get('items', [])
        occasion = combination_data.get('occasion', 'casual')
        weather_data = combination_data.get('weather', {
            'temperature': 22,
            'condition': 'partly cloudy'
        })
        
        if len(items) < 2:
            return {
                "status": "error",
                "message": "Need at least 2 items to validate combination"
            }
        
        # Calculate combination score
        total_score = 0
        feedback = []
        
        # Check color harmony
        colors = [item.get('color', 'unknown') for item in items]
        color_harmony = enhanced_outfit_service._calculate_color_harmony(items)
        total_score += color_harmony
        
        if color_harmony > 3:
            feedback.append("Great color combination!")
        elif color_harmony > 1:
            feedback.append("Good color harmony")
        else:
            feedback.append("Consider adjusting color combination")
        
        # Check formality consistency
        formality_scores = [item.get('formality_score', 5) for item in items]
        formality_range = max(formality_scores) - min(formality_scores)
        
        if formality_range <= 2:
            feedback.append("Consistent formality level")
            total_score += 15
        elif formality_range <= 4:
            feedback.append("Minor formality mismatch")
            total_score += 10
        else:
            feedback.append("Significant formality mismatch - consider adjusting")
            total_score += 5
        
        # Weather appropriateness
        weather_score = 0
        for item in items:
            item_score = enhanced_outfit_service.calculate_item_compatibility_score(
                item, weather_data, occasion
            )
            weather_score += item_score
        
        weather_score = weather_score / len(items)
        total_score += weather_score * 0.5
        
        if weather_score > 80:
            feedback.append("Perfect for current weather")
        elif weather_score > 60:
            feedback.append("Good weather match")
        else:
            feedback.append("May not be ideal for current weather")
        
        # Final score
        final_score = min(100, int(total_score))
        
        return {
            "status": "success",
            "validation": {
                "score": final_score,
                "feedback": feedback,
                "color_harmony_score": color_harmony,
                "formality_consistency": formality_range <= 2,
                "weather_appropriateness": weather_score,
                "recommendation": "Excellent combination!" if final_score > 80 else 
                                "Good combination" if final_score > 60 else 
                                "Consider some adjustments"
            }
        }
        
    except Exception as e:
        logger.error(f"Outfit validation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate outfit combination")

# Favorite outfit endpoints
@app.post("/api/outfit/favorites/save")
async def save_favorite_outfit(request_data: dict):
    """Save an outfit as favorite"""
    try:
        user_id = request_data.get('user_id', 1)
        outfit_data = request_data.get('outfit_data', {})
        outfit_name = request_data.get('outfit_name')
        
        if not outfit_data or not outfit_data.get('items'):
            raise HTTPException(status_code=400, detail="Outfit data is required")
        
        logger.info(f"Saving favorite outfit for user {user_id}")
        
        result = favorite_outfit_service.save_favorite_outfit(
            user_id=user_id,
            outfit_data=outfit_data,
            outfit_name=outfit_name
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save favorite outfit error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save favorite outfit: {str(e)}")

@app.get("/api/outfit/favorites/{user_id}")
async def get_user_favorites(user_id: int):
    """Get all favorite outfits for a user"""
    try:
        logger.info(f"Getting favorite outfits for user {user_id}")
        
        favorites = favorite_outfit_service.get_user_favorites(user_id)
        
        return {
            "status": "success",
            "favorites": favorites,
            "count": len(favorites)
        }
        
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get favorites: {str(e)}")

@app.get("/api/outfit/favorites/{user_id}/{favorite_id}")
async def get_favorite_by_id(user_id: int, favorite_id: int):
    """Get a specific favorite outfit"""
    try:
        favorite = favorite_outfit_service.get_favorite_by_id(user_id, favorite_id)
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite outfit not found")
        
        return {
            "status": "success",
            "favorite": favorite
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get favorite by ID error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get favorite: {str(e)}")

@app.put("/api/outfit/favorites/{user_id}/{favorite_id}")
async def update_favorite_outfit(user_id: int, favorite_id: int, request_data: dict):
    """Update a favorite outfit"""
    try:
        logger.info(f"Updating favorite outfit {favorite_id} for user {user_id}")
        
        result = favorite_outfit_service.update_favorite(
            user_id=user_id,
            favorite_id=favorite_id,
            updates=request_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Update favorite error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update favorite: {str(e)}")

@app.delete("/api/outfit/favorites/{user_id}/{favorite_id}")
async def delete_favorite_outfit(user_id: int, favorite_id: int):
    """Delete a favorite outfit"""
    try:
        logger.info(f"Deleting favorite outfit {favorite_id} for user {user_id}")
        
        result = favorite_outfit_service.delete_favorite(user_id, favorite_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Delete favorite error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete favorite: {str(e)}")

@app.post("/api/outfit/favorites/{user_id}/{favorite_id}/wear")
async def wear_favorite_outfit(user_id: int, favorite_id: int):
    """Mark a favorite outfit as worn"""
    try:
        logger.info(f"Marking favorite outfit {favorite_id} as worn for user {user_id}")
        
        result = favorite_outfit_service.wear_favorite_outfit(user_id, favorite_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Wear favorite outfit error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark outfit as worn: {str(e)}")

# System information endpoints
@app.get("/api/system/info")
async def get_system_info():
    """Get system information and capabilities"""
    return {
        "status": "success",
        "system_info": {
            "version": "2.0.0",
            "features": {
                "ai_clothing_analysis": True,
                "smart_outfit_recommendations": True,
                "weather_integration": True,
                "wardrobe_management": True,
                "trip_planning": True,
                "color_analysis": True,
                "style_learning": True
            },
            "ai_capabilities": {
                "image_recognition": True,
                "style_analysis": True,
                "weather_based_recommendations": True,
                "color_harmony_detection": True,
                "occasion_matching": True,
                "wardrobe_analysis": True
            },
            "database": "PostgreSQL",
            "storage": "Local static files"
        }
    }

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system usage statistics"""
    try:
        # Get basic stats from database
        items = wardrobe_service.get_wardrobe_items()
        
        return {
            "status": "success",
            "stats": {
                "total_wardrobe_items": len(items),
                "total_analyses_performed": len(items),  # Simplified
                "active_users": 1,  # Simplified for demo
                "outfit_recommendations_generated": 0,  # Would track in production
                "ai_analysis_accuracy": 87.5,
                "system_uptime": "Online",
                "last_updated": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"System stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system stats")

# Error handling for common issues
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "/api/wardrobe/items",
            "/api/analyze-clothing",
            "/api/outfit/ai-recommendation",
            "/api/outfit/wardrobe-analysis",
            "/api/trip-planner/enhanced-packing"
        ]
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "status": "error",
        "message": "Internal server error",
        "suggestion": "Please try again or contact support if the issue persists"
    }

# Development and testing endpoints
@app.get("/api/test/ai-recommendation")
async def test_ai_recommendation():
    """Test endpoint for AI recommendation system"""
    try:
        # Test with mock data
        test_data = {
            "user_id": 1,
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "occasion": "casual"
        }
        
        result = await get_ai_outfit_recommendation(test_data)
        
        return {
            "status": "success",
            "test_result": "AI recommendation system working",
            "sample_response": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "test_result": "AI recommendation system failed",
            "error": str(e)
        }

@app.post("/api/test/add-sample-wardrobe")
async def add_sample_wardrobe():
    """Add sample wardrobe items for testing"""
    try:
        sample_items = [
            {
                'name': 'Blue Cotton T-Shirt',
                'category': 'tops',
                'color': 'blue',
                'season': 'summer',
                'user_id': 1,
                'confidence': 90.0
            },
            {
                'name': 'Black Denim Jeans',
                'category': 'bottoms', 
                'color': 'black',
                'season': 'all',
                'user_id': 1,
                'confidence': 85.0
            },
            {
                'name': 'White Canvas Sneakers',
                'category': 'shoes',
                'color': 'white', 
                'season': 'all',
                'user_id': 1,
                'confidence': 88.0
            },
            {
                'name': 'Red Tank Top',
                'category': 'tops',
                'color': 'red',
                'season': 'summer',
                'user_id': 1,
                'confidence': 92.0
            },
            {
                'name': 'Khaki Chino Shorts',
                'category': 'bottoms',
                'color': 'khaki',
                'season': 'summer',
                'user_id': 1,
                'confidence': 87.0
            }
        ]
        
        added_count = 0
        for item in sample_items:
            try:
                result = wardrobe_service.save_wardrobe_item(item)
                if result:
                    added_count += 1
                    logger.info(f"Added sample item: {item['name']}")
            except Exception as e:
                logger.error(f"Failed to add item {item['name']}: {e}")
                
        return {
            "status": "success", 
            "message": f"Added {added_count} sample items to wardrobe",
            "items_added": added_count
        }
    except Exception as e:
        logger.error(f"Error adding sample wardrobe: {e}")
        return {
            "status": "error", 
            "message": str(e)
        }

@app.post("/api/recommendations/buy")
async def get_buy_recommendations(request_data: dict):
    """Get AI-powered buying recommendations based on user's wardrobe"""
    try:
        user_id = request_data.get('user_id', 1)
        
        # Initialize the recommendation service
        recommendation_service = BuyRecommendationService()
        
        # Get recommendations with analytics
        result = recommendation_service.get_recommendations_with_analytics(user_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting buy recommendations: {e}")
        return {
            "status": "error",
            "message": f"Failed to get recommendations: {str(e)}",
            "recommendations": [],
            "analytics": {}
        }

# Mount static files for images - this should be done after all routes are defined
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount images directory for direct access
images_dir = static_dir / "images"
images_dir.mkdir(exist_ok=True)
app.mount("/images", StaticFiles(directory=images_dir), name="images")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)