from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
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
from database.connection import DatabaseConnection
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import json
import glob
import uuid
from pathlib import Path
import re

# Load environment variables
load_dotenv()

# Configure static directory
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database connection
db = DatabaseConnection()

# JWT and Auth imports
from utils.jwt_utils import verify_password, get_password_hash, create_access_token
from utils.auth_dependencies import get_current_user, get_current_user_optional

# Initialize services
trip_ai_service = None
outfit_history_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    # Startup
    global trip_ai_service, outfit_history_service
    
    try:
        # Create users table if it doesn't exist
        create_users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        db.execute_query(create_users_table_sql)
        logger.info("Users table created/verified")
        
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
    description="Backend API with JWT Authentication, AI Clothing Analysis, Trip Planning, and Smart Outfit Recommendations",
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
            "authentication": "JWT",
            "storage": "Static Files Only",
            "features": [
                "JWT Authentication",
                "User Registration & Login",
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
            
            # Test users table
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            health_status["services"]["database"] = {
                "status": "connected",
                "version": version[:50],
                "user_count": user_count
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
    
    # Check authentication
    try:
        health_status["services"]["authentication"] = {
            "status": "ready",
            "jwt_enabled": True,
            "token_expiry": "7 days"
        }
    except Exception as e:
        health_status["services"]["authentication"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_status

# Authentication Endpoints
@app.post("/auth/signup")
async def signup(user_data: dict):
    """JWT-based user signup - saves to database"""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        name = user_data.get("name")
        
        # Validation
        if not email or not password or not name:
            raise HTTPException(status_code=400, detail="Name, email and password are required")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        if len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        
        # Basic email format validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check if user already exists
        try:
            check_user_query = "SELECT id FROM users WHERE email = %s LIMIT 1;"
            existing_user = db.execute_query(check_user_query, (email,))
            
            if existing_user:
                raise HTTPException(status_code=409, detail="User with this email already exists")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database check error: {e}")
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user in database
        try:
            insert_query = """
                INSERT INTO users (email, username, hashed_password, full_name, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, email, username, full_name;
            """
            result = db.execute_query(insert_query, (
                email,
                name,
                hashed_password,
                name,
                True,
                datetime.now()
            ))
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to create user")
            
            new_user = result if isinstance(result, dict) else result[0] if result else None
            
            logger.info(f"User created successfully: {name} <{email}> (id={new_user['id']})")
            
            # Create JWT token for auto-login after signup
            access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
            access_token = create_access_token(
                data={
                    "sub": str(new_user['id']),  # Ensure sub is string for JWT spec compliance
                    "email": new_user['email'], 
                    "name": new_user['full_name'] or new_user['username']
                },
                expires_delta=access_token_expires
            )
            
            # Return success with auto-login token
            return {
                "status": "success",
                "message": "Account created successfully!",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 60 * 24 * 7 * 60,  # seconds
                "user": {
                    "id": new_user['id'],
                    "email": new_user['email'],
                    "name": new_user['full_name'],
                    "username": new_user['username']
                }
            }
            
        except Exception as e:
            logger.exception("Database insert error")
            raise HTTPException(status_code=500, detail="Failed to create user account")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Signup error")
        raise HTTPException(status_code=500, detail="Signup failed")

@app.post("/auth/login")
async def login(credentials: dict):
    """JWT-based user login - checks database"""
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        # Basic email format validation
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Get user from database
        try:
            user_query = """
                SELECT id, email, username, hashed_password, full_name, is_active 
                FROM users 
                WHERE email = %s 
                LIMIT 1;
            """
            user_result = db.execute_query(user_query, (email,))
            
            if not user_result:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            user = user_result[0] if isinstance(user_result, list) else user_result
            
            # Check if user is active
            if not user.get('is_active', True):
                raise HTTPException(status_code=401, detail="Account is deactivated")
            
            # Verify password
            if not verify_password(password, user['hashed_password']):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Create JWT token
            access_token_expires = timedelta(minutes=60 * 24 * 7)  # 7 days
            access_token = create_access_token(
                data={
                    "sub": str(user['id']),  # Ensure sub is string for JWT spec compliance
                    "email": user['email'], 
                    "name": user.get('full_name') or user.get('username')
                },
                expires_delta=access_token_expires
            )
            
            user_data = {
                "id": int(user['id']),
                "email": user['email'],
                "name": user.get('full_name') or user.get('username'),
                "username": user.get('username')
            }
            
            logger.info(f"Successful JWT login for user: {email}")
            
            return {
                "status": "success",
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 60 * 24 * 7 * 60,  # seconds
                "user": user_data
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise HTTPException(status_code=500, detail="Login failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/verify")
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return user info"""
    try:
        # Get fresh user data from database
        user_query = """
            SELECT id, email, username, full_name, is_active 
            FROM users 
            WHERE id = %s 
            LIMIT 1;
        """
        user_result = db.execute_query(user_query, (current_user["user_id"],))
        
        if not user_result:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = user_result[0] if isinstance(user_result, list) else user_result
        
        if not user.get('is_active', True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        user_data = {
            "id": int(user['id']),
            "email": user['email'],
            "name": user.get('full_name') or user.get('username'),
            "username": user.get('username')
        }
        
        return {
            "status": "success",
            "message": "Token is valid",
            "user": user_data
        }
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/logout")
async def logout():
    """Logout endpoint - JWT is stateless, so client should discard token"""
    return {
        "status": "success",
        "message": "Logged out successfully. Please discard your token."
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    try:
        # Get fresh user data from database
        user_query = """
            SELECT id, email, username, full_name, is_active 
            FROM users 
            WHERE id = %s 
            LIMIT 1;
        """
        user_result = db.execute_query(user_query, (current_user["user_id"],))
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_result[0] if isinstance(user_result, list) else user_result
        
        user_data = {
            "id": int(user['id']),
            "email": user['email'],
            "name": user.get('full_name') or user.get('username'),
            "username": user.get('username')
        }
        
        return {
            "status": "success",
            "user": user_data
        }
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

# Protected Wardrobe Endpoints

@app.get("/api/wardrobe/items")
async def get_wardrobe_items(current_user: dict = Depends(get_current_user)):
    """Get user's wardrobe items (protected)"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Getting wardrobe items for user: {user_id}")
        
        # FIX: Pass user_id to filter by user
        items = wardrobe_service.get_wardrobe_items(user_id=user_id)
        
        logger.info(f"Retrieved {len(items)} items from wardrobe service")
        return {
            "status": "success",
            "items": items,
            "user_id": user_id
        }
    except Exception as e:
        logger.exception("Get wardrobe items error")
        raise HTTPException(status_code=500, detail="Failed to retrieve wardrobe items")
    
@app.post("/api/wardrobe/items")
async def add_wardrobe_item(item_data: dict, current_user: dict = Depends(get_current_user)):
    """Add item to wardrobe with smart image path detection (protected)"""
    global last_analyzed_image
    
    try:
        user_id = current_user["user_id"]
        logger.info(f"Adding wardrobe item for user {user_id}: {item_data.get('name', 'Unknown')}")
        
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
        
        # Set the final image path and user_id
        item_data['image_path'] = image_path
        item_data['user_id'] = user_id
        logger.info(f"Final image_path for database: {image_path}")
        
        # Map analysis fields to database fields
        if 'suggestedCategory' in item_data:
            item_data['category'] = item_data.pop('suggestedCategory')
        if 'suggestedColor' in item_data:
            item_data['color'] = item_data.pop('suggestedColor')
        if 'suggestedOccasion' in item_data:
            item_data.pop('suggestedOccasion')
        if 'season' not in item_data or not item_data['season']:
            item_data['season'] = 'all'
        
        # Save item to database
        logger.info(f"About to save wardrobe item with data: {item_data}")
        result = wardrobe_service.save_wardrobe_item(item_data)
        logger.info(f"Save result: {result}")
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
            logger.error("Failed to save item to database - result is None")
            raise HTTPException(status_code=500, detail="Failed to save item to database")
            
    except Exception as e:
        logger.exception(f"Add wardrobe item error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add item")

@app.delete("/api/wardrobe/items/{item_id}")
async def delete_wardrobe_item(item_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a wardrobe item (protected)"""
    try:
        user_id = current_user["user_id"]
        
        # Get the item first to clean up the image
        item = wardrobe_service.get_wardrobe_item_by_id(item_id)
        if item and item.get('image_path'):
            # Delete the image file
            image_storage_service.delete_image(item['image_path'])
        
        success = wardrobe_service.delete_wardrobe_item(item_id)
        if success:
            return {
                "status": "success",
                "message": "Item deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Delete wardrobe item error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")

@app.get("/api/outfit/history")
async def get_outfit_history(
    user_id: int = None,
    limit: int = 50, 
    start_date: str = None, 
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get user's outfit history (protected)"""
    try:
        # Use the authenticated user's ID if no user_id provided, or verify access
        if user_id is None:
            user_id = current_user["user_id"]
        elif current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Getting outfit history for user {user_id}")
        
        if outfit_history_service:
            result = outfit_history_service.get_user_outfit_history(
                user_id=user_id,
                limit=limit,
                start_date=start_date,
                end_date=end_date
            )
            
            return {
                "status": "success",
                "history": result.get('history', []),
                "count": len(result.get('history', [])),
                "user_id": user_id
            }
        else:
            # Service not available, return empty history
            logger.warning("Outfit history service not available")
            return {
                "status": "success",
                "history": [],
                "count": 0,
                "user_id": user_id,
                "message": "Outfit history tracking not available"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get outfit history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get outfit history")
    

# Favorite Outfit Routes (Protected)
@app.get("/api/favorites")
async def get_user_favorites(current_user: dict = Depends(get_current_user)):
    """Get user's favorite outfits (protected)"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Getting favorites for user {user_id}")
        
        # Use the favorite outfit service
        favorites = favorite_outfit_service.get_user_favorites(user_id)
        
        return {
            "status": "success",
            "favorites": favorites,
            "count": len(favorites),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get favorites")

@app.post("/api/favorites")
async def save_favorite_outfit(favorite_data: dict, current_user: dict = Depends(get_current_user)):
    """Save outfit as favorite (protected)"""
    try:
        user_id = current_user["user_id"]
        favorite_data['user_id'] = user_id  # Ensure favorite belongs to authenticated user
        logger.info(f"Saving favorite for user {user_id}: {favorite_data.get('name', 'Unknown')}")
        
        # Use the favorite outfit service
        result = favorite_outfit_service.save_favorite(favorite_data)
        
        if result.get('success'):
            return {
                "status": "success",
                "favorite_id": result["id"],
                "message": "Favorite saved successfully",
                "user_id": user_id
            }
        else:
            logger.error(f"Service returned error: {result}")
            raise HTTPException(status_code=500, detail=result.get('message', 'Failed to save favorite'))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save favorite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save favorite")

@app.delete("/api/favorites/{favorite_id}")
async def delete_favorite_outfit(favorite_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a favorite outfit (protected)"""
    try:
        user_id = current_user["user_id"]
        
        # Verify the favorite belongs to the user
        favorite = favorite_outfit_service.get_favorite_by_id(favorite_id)
        if not favorite or favorite.get('user_id') != user_id:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        success = favorite_outfit_service.delete_favorite(favorite_id)
        if success:
            return {
                "status": "success",
                "message": "Favorite deleted successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete favorite")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete favorite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete favorite")

@app.get("/api/favorites/{favorite_id}")
async def get_favorite_outfit(favorite_id: int, current_user: dict = Depends(get_current_user)):
    """Get specific favorite outfit (protected)"""
    try:
        user_id = current_user["user_id"]
        
        favorite = favorite_outfit_service.get_favorite_by_id(favorite_id)
        if not favorite or favorite.get('user_id') != user_id:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        return {
            "status": "success",
            "favorite": favorite
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get favorite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get favorite")
    
@app.post("/api/favorites/{favorite_id}/wear")
async def wear_favorite_outfit(favorite_id: int, current_user: dict = Depends(get_current_user)):
    """Mark a favorite outfit as worn (protected)"""
    try:
        user_id = current_user["user_id"]
        
        # Verify the favorite belongs to the user
        favorite = favorite_outfit_service.get_favorite_by_id(favorite_id)
        if not favorite or favorite.get('user_id') != user_id:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        result = favorite_outfit_service.wear_favorite_outfit(favorite_id)
        if result['success']:
            return {
                "status": "success",
                "message": result['message']
            }
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wear favorite error: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark favorite as worn")

@app.get("/api/wardrobe/stats")
async def get_wardrobe_stats(current_user: dict = Depends(get_current_user)):
    """Get wardrobe statistics (protected)"""
    try:
        user_id = current_user["user_id"]
        items = wardrobe_service.get_wardrobe_items()  # Pass user_id in production
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
                "ai_analysis_accuracy": 0.87,
                "user_id": user_id
            }
        }
    except Exception as e:
        logger.error(f"Get wardrobe stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# AI Analysis Routes (Authentication Optional for Analysis, Required for Saving)
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

# AI Outfit Recommendation Routes (Protected)
@app.post("/api/outfit/ai-recommendation")
async def get_ai_outfit_recommendation(request_data: dict, current_user: dict = Depends(get_current_user)):
    """Generate AI outfit recommendation from user's actual wardrobe (protected)"""
    try:
        user_id = current_user["user_id"]
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
            "message": "AI recommendation generated from your wardrobe",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"AI outfit recommendation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI recommendation: {str(e)}")

@app.get("/api/outfit/wardrobe-analysis/{user_id}")
async def analyze_user_wardrobe(user_id: int, current_user: dict = Depends(get_current_user)):
    """Analyze user's wardrobe for AI insights (protected)"""
    try:
        # Ensure user can only access their own wardrobe analysis
        if current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
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

# Additional protected endpoints following the same pattern...

@app.post("/api/outfit/multiple-recommendations")
async def get_multiple_outfit_recommendations(request_data: dict, current_user: dict = Depends(get_current_user)):
    """Generate multiple AI outfit recommendations for different occasions (protected)"""
    try:
        user_id = current_user["user_id"]
        location = request_data.get('location', {})
        occasions = request_data.get('occasions', ['casual', 'work', 'formal', 'workout', 'datenight'])
        demo_weather = request_data.get('demo_weather')
        
        # Weather data processing (same as above)
        if demo_weather:
            weather_data = {
                'temperature': demo_weather.get('temperature', 25),
                'condition': demo_weather.get('condition', 'sunny'),
                'humidity': demo_weather.get('humidity', 60),
                'windSpeed': demo_weather.get('windSpeed', 10),
                'precipitation': demo_weather.get('precipitation', 0),
                'location': demo_weather.get('location', 'Demo Location')
            }
        else:
            weather_data = {
                'temperature': 22,
                'condition': 'partly cloudy',
                'humidity': 55,
                'windSpeed': 12,
                'precipitation': 0
            }
        
        # Use the enhanced multi-occasion service
        result = enhanced_outfit_service.generate_multi_occasion_recommendations(
            user_id=user_id,
            weather_data=weather_data
        )
        
        if result.get('error'):
            return {
                "status": "error",
                "message": result['message'],
                "recommendations": {}
            }
        
        return {
            "status": "success",
            "recommendations": result['recommendations'],
            "wardrobe_analysis": result['wardrobe_analysis'],
            "weather": weather_data,
            "message": f"Generated outfit recommendations for all occasions",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Multiple recommendations error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate multiple recommendations")

@app.post("/api/outfit/wear")
async def record_worn_outfit(request_data: dict, current_user: dict = Depends(get_current_user)):
    """Record when a user wears an outfit (protected)"""
    try:
        user_id = current_user["user_id"]
        outfit_data = request_data.get('outfit_data', {})
        occasion = request_data.get('occasion', 'casual')
        weather = request_data.get('weather', '')
        location = request_data.get('location', '')
        worn_date = request_data.get('worn_date', datetime.now().date())
        
        logger.info(f"Recording worn outfit for user {user_id}")
        logger.info(f"Outfit data: {outfit_data}")
        
        # Validate outfit data
        if not outfit_data or not outfit_data.get('items'):
            raise HTTPException(status_code=400, detail="Outfit data and items are required")
        
        # Use outfit history service if available
        if outfit_history_service:
            try:
                result = outfit_history_service.record_worn_outfit(
                    user_id=user_id,
                    outfit_data=outfit_data,
                    occasion=occasion,
                    weather=weather,
                    location=location,
                    worn_date=worn_date
                )
                
                if result:
                    return {
                        "status": "success",
                        "message": "Outfit wear recorded successfully",
                        "outfit_id": result.get('outfit_id'),
                        "worn_date": str(worn_date),
                        "user_id": user_id
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to record outfit wear")
                    
            except Exception as e:
                logger.error(f"Outfit history service error: {e}")
                # Fall back to simple response
                return {
                    "status": "success",
                    "message": "Outfit noted (limited tracking)",
                    "user_id": user_id,
                    "fallback": True
                }
        else:
            # Outfit history service not available, return success anyway
            logger.warning("Outfit history service not available")
            return {
                "status": "success", 
                "message": "Outfit noted (tracking disabled)",
                "user_id": user_id,
                "service_available": False
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Record worn outfit error")
        raise HTTPException(status_code=500, detail="Failed to record outfit wear")

# Trip Planning Routes (Protected)
@app.post("/api/trip-planner/enhanced-packing")
async def enhanced_packing_recommendations(request_data: dict, current_user: dict = Depends(get_current_user)):
    """Generate enhanced packing recommendations with wardrobe integration (protected)"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing enhanced packing request for user {user_id}...")
        
        trip_details = request_data.get('tripDetails', {})
        wardrobe_items = request_data.get('wardrobeItems', [])
        duration = request_data.get('duration', 7)
        
        logger.info(f"Trip destination: {trip_details.get('destination', 'Unknown')}")
        logger.info(f"Activities: {trip_details.get('activities', [])}")
        logger.info(f"Weather: {trip_details.get('weatherExpected', 'Unknown')}")
        logger.info(f"Wardrobe items count: {len(wardrobe_items)}")
        logger.info(f"Duration: {duration}")
        
        # Use the AI trip generator for intelligent analysis
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
            "message": "Smart packing list generated with AI analysis",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Enhanced packing recommendations error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate enhanced recommendations: {str(e)}")

@app.get("/api/trips")
async def get_user_trips(current_user: dict = Depends(get_current_user)):
    """Get user's saved trips (protected)"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Getting trips for user: {user_id}")
        
        # Use the trip service to get from database
        trips = trip_service.get_user_trips(user_id)
        
        return {
            "status": "success",
            "trips": trips,
            "count": len(trips),
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Get trips error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trips: {str(e)}")

@app.post("/api/trips")
async def save_trip(trip_data: dict, current_user: dict = Depends(get_current_user)):
    """Save trip details and packing list (protected)"""
    try:
        user_id = current_user["user_id"]
        trip_data['user_id'] = user_id  # Ensure trip belongs to authenticated user
        logger.info(f"Saving trip for user {user_id}: {trip_data.get('destination', 'Unknown')}")
        
        # Use the trip service to save to database
        result = trip_service.save_trip(trip_data)
        
        return {
            "status": "success",
            "trip_id": result["id"],
            "message": "Trip saved successfully to database",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Save trip error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save trip: {str(e)}")

# Weather Integration
@app.get("/api/weather/{lat}/{lon}")
async def get_weather_data(lat: float, lon: float):
    """Get weather data for coordinates (public endpoint)"""
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

# System Information (Public)
@app.get("/api/system/info")
async def get_system_info():
    """Get system information and capabilities"""
    return {
        "status": "success",
        "system_info": {
            "version": "2.0.0",
            "authentication": "JWT",
            "features": {
                "user_authentication": True,
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

# Testing endpoints (Development only)
@app.post("/api/test/add-sample-wardrobe")
async def add_sample_wardrobe(current_user: dict = Depends(get_current_user)):
    """Add sample wardrobe items for testing (protected)"""
    try:
        user_id = current_user["user_id"]
        
        sample_items = [
            {
                'name': 'Blue Cotton T-Shirt',
                'category': 'tops',
                'color': 'blue',
                'season': 'summer',
                'user_id': user_id,
                'confidence': 90.0
            },
            {
                'name': 'Black Denim Jeans',
                'category': 'bottoms', 
                'color': 'black',
                'season': 'all',
                'user_id': user_id,
                'confidence': 85.0
            },
            {
                'name': 'White Canvas Sneakers',
                'category': 'shoes',
                'color': 'white', 
                'season': 'all',
                'user_id': user_id,
                'confidence': 88.0
            },
            {
                'name': 'Red Tank Top',
                'category': 'tops',
                'color': 'red',
                'season': 'summer',
                'user_id': user_id,
                'confidence': 92.0
            },
            {
                'name': 'Khaki Chino Shorts',
                'category': 'bottoms',
                'color': 'khaki',
                'season': 'summer',
                'user_id': user_id,
                'confidence': 87.0
            }
        ]
        
        added_count = 0
        for item in sample_items:
            try:
                result = wardrobe_service.save_wardrobe_item(item)
                if result:
                    added_count += 1
                    logger.info(f"Added sample item for user {user_id}: {item['name']}")
            except Exception as e:
                logger.error(f"Failed to add item {item['name']}: {e}")
                
        return {
            "status": "success", 
            "message": f"Added {added_count} sample items to wardrobe",
            "items_added": added_count,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error adding sample wardrobe: {e}")
        return {
            "status": "error", 
            "message": str(e)
        }

# Mount static files for images - this should be done after all routes are defined
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount images directory for direct access
images_dir = static_dir / "images"
images_dir.mkdir(exist_ok=True)
app.mount("/images", StaticFiles(directory=images_dir), name="images")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)