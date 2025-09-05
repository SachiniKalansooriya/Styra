# Backend/main.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import psycopg2
import os
import logging
import uvicorn
from dotenv import load_dotenv
from image_analysis import image_analysis_service
from datetime import datetime
import json

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            "database": "Supabase PostgreSQL",
            "ai_analysis": ai_status,
            "features": [
                "Free AI Clothing Analysis",
                "Automatic Category Detection",
                "Color Recognition",
                "Offline Capability"
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

# Authentication Routes
@app.post("/auth/login")
async def login(credentials: dict):
    """User login endpoint"""
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        # TODO: Implement real authentication with database
        # For now, return mock successful login
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
        
        # TODO: Implement real user creation with database
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
@app.get("/wardrobe/items")
async def get_wardrobe_items(user_id: int = 1):
    """Get user's wardrobe items"""
    try:
        # TODO: Implement real database queries
        # Mock wardrobe items for now
        return {
            "status": "success",
            "items": [
                {
                    "id": 1,
                    "name": "Blue Denim Jeans",
                    "category": "bottoms",
                    "color": "Blue",
                    "season": "all",
                    "image_url": None,
                    "last_worn": None,
                    "times_worn": 5,
                    "confidence": 0.9,
                    "analysis_method": "ai_analysis"
                },
                {
                    "id": 2,
                    "name": "White Cotton T-Shirt",
                    "category": "tops",
                    "color": "White",
                    "season": "summer",
                    "image_url": None,
                    "last_worn": "2025-09-01",
                    "times_worn": 8,
                    "confidence": 0.85,
                    "analysis_method": "ai_analysis"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Get wardrobe items error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve wardrobe items")

@app.post("/wardrobe/items")
async def add_wardrobe_item(item_data: dict):
    """Add item to wardrobe"""
    try:
        # TODO: Implement real database storage
        return {
            "status": "success",
            "message": "Item added to wardrobe",
            "item": {
                "id": 3,
                "created_at": datetime.now().isoformat(),
                **item_data
            }
        }
    except Exception as e:
        logger.error(f"Add wardrobe item error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add item")

@app.get("/wardrobe/stats")
async def get_wardrobe_stats(user_id: int = 1):
    """Get wardrobe statistics"""
    try:
        # TODO: Calculate real stats from database
        return {
            "status": "success",
            "stats": {
                "total_items": 25,
                "categories": {
                    "tops": 8,
                    "bottoms": 6,
                    "dresses": 4,
                    "shoes": 5,
                    "accessories": 2
                },
                "colors": {
                    "Blue": 6,
                    "Black": 5,
                    "White": 4,
                    "Red": 3,
                    "Gray": 2
                },
                "most_worn_category": "tops",
                "least_worn_category": "accessories",
                "ai_analysis_accuracy": 0.87
            }
        }
    except Exception as e:
        logger.error(f"Get wardrobe stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# AI Analysis Routes
@app.post("/api/analyze-clothing")
async def analyze_clothing_image(image: UploadFile = File(...)):
    """Analyze clothing item from uploaded image using free AI"""
    try:
        logger.info(f"Analyzing clothing image: {image.filename}")
        
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        image_data = await image.read()
        
        if len(image_data) > max_size:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")
        
        # Analyze the image using free AI
        logger.info("Starting AI analysis...")
        analysis_result = image_analysis_service.analyze_clothing_item(image_data)
        
        logger.info(f"Analysis completed: {analysis_result.get('analysis_method')} - {analysis_result.get('confidence', 0):.2f}")
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "message": "Image analyzed successfully",
            "processing_info": {
                "file_size": len(image_data),
                "file_type": image.content_type,
                "analysis_time": analysis_result.get('processing_time', 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/wardrobe/items")
async def add_wardrobe_item_with_analysis(
    name: str = Form(...),
    category: str = Form(None),
    color: str = Form(None),
    season: str = Form("all"),
    image: UploadFile = File(None)
):
    """Add wardrobe item with optional image analysis"""
    try:
        item_data = {
            "name": name,
            "category": category,
            "color": color,
            "season": season,
            "analysis_result": None
        }
        
        # If image provided, analyze it
        if image and image.content_type.startswith('image/'):
            logger.info(f"Analyzing uploaded image for new wardrobe item")
            
            image_data = await image.read()
            analysis_result = image_analysis_service.analyze_clothing_item(image_data)
            
            # Use AI suggestions if not provided manually
            if not category:
                item_data["category"] = analysis_result.get("suggestedCategory", "tops")
            if not color:
                item_data["color"] = analysis_result.get("suggestedColor", "Unknown")
            
            item_data["analysis_result"] = analysis_result
            item_data["confidence"] = analysis_result.get("confidence", 0.5)
            item_data["analysis_method"] = analysis_result.get("analysis_method", "manual")
        
        # TODO: Save to database
        response_item = {
            "id": abs(hash(name + str(datetime.now()))) % 10000,
            "created_at": datetime.now().isoformat(),
            **item_data
        }
        
        return {
            "status": "success",
            "message": "Item added to wardrobe successfully",
            "item": response_item
        }
        
    except Exception as e:
        logger.error(f"Failed to add wardrobe item: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add item: {str(e)}")

# AI Service Information
@app.get("/api/ai/status")
async def get_ai_service_status():
    """Get AI service status and capabilities"""
    try:
        status = image_analysis_service.get_service_info()
        return {
            "status": "success",
            "ai_service": status,
            "capabilities": {
                "image_analysis": True,
                "category_detection": True,
                "color_recognition": True,
                "offline_mode": status.get('ai_models_loaded', False),
                "supported_formats": ["JPEG", "PNG", "WEBP"]
            }
        }
    except Exception as e:
        logger.error(f"AI status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI status")

# Outfit Routes
@app.post("/outfits/recommendations")
async def get_outfit_recommendations(preferences: dict):
    """Get AI outfit recommendations"""
    try:
        # TODO: Implement real AI outfit recommendations
        weather = preferences.get("weather", "sunny")
        occasion = preferences.get("occasion", "casual")
        
        return {
            "status": "success",
            "outfits": [
                {
                    "id": 1,
                    "name": f"{occasion.title()} {weather.title()} Outfit",
                    "items": ["White T-Shirt", "Blue Jeans", "White Sneakers"],
                    "confidence": 92,
                    "reason": f"Perfect for {weather} weather and {occasion} occasions",
                    "ai_generated": True
                },
                {
                    "id": 2,
                    "name": "Alternative Option",
                    "items": ["Blue Shirt", "Dark Pants", "Black Shoes"],
                    "confidence": 88,
                    "reason": "Versatile combination for various settings",
                    "ai_generated": True
                }
            ],
            "preferences_used": preferences
        }
    except Exception as e:
        logger.error(f"Outfit recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# Weather Routes
@app.get("/weather/current")
async def get_current_weather(location: str = "Polonnaruwa"):
    """Get current weather for outfit recommendations"""
    try:
        # TODO: Integrate real weather API
        return {
            "status": "success",
            "weather": {
                "temperature": 28,
                "condition": "sunny",
                "description": "Sunny",
                "humidity": 45,
                "location": location,
                "recommendations": {
                    "clothing_weight": "light",
                    "colors": ["light", "bright"],
                    "materials": ["cotton", "linen"]
                }
            }
        }
    except Exception as e:
        logger.error(f"Weather error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weather")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "status": "error",
        "message": "Endpoint not found",
        "detail": "The requested endpoint does not exist"
    }

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"Server error: {exc}")
    return {
        "status": "error",
        "message": "Internal server error",
        "detail": "An unexpected error occurred"
    }

# In your main.py, update the health_check function:

@app.get("/health")
async def health_check():
    """Comprehensive health check with local database"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check local database
    try:
        from database.connection import db
        db_status = db.test_connection()
        health_status["services"]["database"] = {
            "status": db_status["status"],
            "type": "local_postgresql",
            "version": db_status.get("version", "unknown")[:50] if db_status["status"] == "connected" else None
        }
        
        if db_status["status"] != "connected":
            health_status["status"] = "degraded"
            
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # AI service check remains the same...
    
    return health_status

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)