from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Styra AI Wardrobe Backend",
    description="Backend API with Supabase",
    version="1.0.0"
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
    return {
        "message": "Styra AI Wardrobe API", 
        "status": "running", 
        "database": "Supabase PostgreSQL"
    }

@app.get("/health")
async def health_check():
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            return {"status": "unhealthy", "error": "DATABASE_URL not configured"}
            
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy", 
            "database": "connected", 
            "version": version[:50]
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# User Authentication Routes
@app.post("/auth/login")
async def login(credentials: dict):
    # Mock login - replace with real authentication
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Mock successful login
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

@app.post("/auth/signup")
async def signup(user_data: dict):
    # Mock signup - replace with real user creation
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

# Wardrobe Routes
@app.get("/wardrobe/items")
async def get_wardrobe_items():
    # Mock wardrobe items
    return {
        "status": "success",
        "items": [
            {
                "id": 1,
                "name": "Blue Denim Jeans",
                "category": "Bottoms",
                "color": "Blue",
                "season": "All",
                "image_url": None,
                "last_worn": None,
                "times_worn": 5
            },
            {
                "id": 2,
                "name": "White Cotton T-Shirt",
                "category": "Tops",
                "color": "White", 
                "season": "Summer",
                "image_url": None,
                "last_worn": "2025-09-01",
                "times_worn": 8
            }
        ]
    }

@app.post("/wardrobe/items")
async def add_wardrobe_item(item_data: dict):
    # Mock add item
    return {
        "status": "success",
        "message": "Item added to wardrobe",
        "item": {
            "id": 3,
            **item_data
        }
    }

@app.get("/wardrobe/stats")
async def get_wardrobe_stats():
    return {
        "status": "success",
        "stats": {
            "total_items": 25,
            "categories": {
                "Tops": 8,
                "Bottoms": 6,
                "Dresses": 4,
                "Shoes": 5,
                "Accessories": 2
            },
            "most_worn_category": "Tops",
            "least_worn_category": "Accessories"
        }
    }

# Outfit Routes
@app.post("/outfits/recommendations")
async def get_outfit_recommendations(preferences: dict):
    return {
        "status": "success",
        "outfits": [
            {
                "id": 1,
                "name": "Casual Day Out",
                "items": ["White T-Shirt", "Blue Jeans", "White Sneakers"],
                "confidence": 92,
                "reason": "Perfect for comfortable daily activities"
            },
            {
                "id": 2,
                "name": "Business Casual",
                "items": ["Blue Shirt", "Dark Pants", "Black Shoes"],
                "confidence": 88,
                "reason": "Professional look for work"
            }
        ]
    }

# Weather Routes  
@app.get("/weather/current")
async def get_current_weather():
    return {
        "status": "success",
        "weather": {
            "temperature": 28,
            "condition": "sunny",
            "description": "Sunny",
            "humidity": 45,
            "location": "Negombo, Western Province"
        }
    }