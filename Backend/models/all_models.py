# Backend/app/models/all_models.py
"""
Consolidated database models for Styra AI Wardrobe App
This file contains all database table definitions using SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums for better data consistency
class PackingStyle(enum.Enum):
    MINIMAL = "minimal"
    COMFORT = "comfort" 
    FASHION = "fashion"
    BUSINESS = "business"

class Season(enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    ALL = "all"

class Occasion(enum.Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    BUSINESS = "business"
    ATHLETIC = "athletic"
    BEACHWEAR = "beachwear"
    PARTY = "party"
    DATENIGHT = "datenight"
    SEASONAL = "seasonal"

# User Management
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    wardrobe_items = relationship("WardrobeItem", back_populates="user", cascade="all, delete-orphan")
    outfit_history = relationship("OutfitHistory", back_populates="user", cascade="all, delete-orphan")
    favorite_outfits = relationship("FavoriteOutfit", back_populates="user", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")

# Wardrobe Management
class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    color = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    season = Column(Enum(Season), default=Season.ALL)
    occasion = Column(Enum(Occasion), default=Occasion.CASUAL)
    image_url = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)  # Local storage path
    times_worn = Column(Integer, default=0)
    date_added = Column(DateTime, server_default=func.now())
    pending_sync = Column(Boolean, default=False)
    
    # AI-generated metadata
    ai_tags = Column(JSON, nullable=True)  # Store AI-generated tags
    style_confidence = Column(Float, nullable=True)  # AI confidence score
    
    # Relationships
    user = relationship("User", back_populates="wardrobe_items")
    outfit_items = relationship("OutfitItem", back_populates="wardrobe_item", cascade="all, delete-orphan")

# Outfit History
class OutfitHistory(Base):
    __tablename__ = "outfit_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worn_date = Column(DateTime, nullable=False)
    occasion = Column(Enum(Occasion), nullable=True)
    weather = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    confidence_score = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)  # User rating 1-5
    notes = Column(Text, nullable=True)
    outfit_data = Column(JSON, nullable=True)  # Store complete outfit data
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="outfit_history")
    outfit_items = relationship("OutfitItem", back_populates="outfit_history", cascade="all, delete-orphan")

class OutfitItem(Base):
    __tablename__ = "outfit_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    outfit_history_id = Column(Integer, ForeignKey("outfit_history.id"), nullable=True)
    favorite_outfit_id = Column(Integer, ForeignKey("favorite_outfits.id"), nullable=True)
    wardrobe_item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=False)
    
    # Relationships
    outfit_history = relationship("OutfitHistory", back_populates="outfit_items")
    favorite_outfit = relationship("FavoriteOutfit", back_populates="outfit_items")
    wardrobe_item = relationship("WardrobeItem", back_populates="outfit_items")

# Favorite Outfits
class FavoriteOutfit(Base):
    __tablename__ = "favorite_outfits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    occasion = Column(Enum(Occasion), nullable=True)
    confidence_score = Column(Float, nullable=True)
    times_worn = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    weather_context = Column(JSON, nullable=True)  # Store weather when saved
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="favorite_outfits")
    outfit_items = relationship("OutfitItem", back_populates="favorite_outfit", cascade="all, delete-orphan")

# Trip Planning
class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    activities = Column(JSON, nullable=True)  # List of planned activities
    weather_expected = Column(String(100), nullable=True)
    packing_style = Column(Enum(PackingStyle), default=PackingStyle.MINIMAL)
    packing_list = Column(JSON, nullable=True)  # Complete packing recommendations
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="trips")

# AI Analysis and Recommendations
class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String(100), nullable=False)  # 'wardrobe_analysis', 'outfit_recommendation', etc.
    input_data = Column(JSON, nullable=True)  # Input parameters
    result_data = Column(JSON, nullable=True)  # AI analysis results
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analysis_history")

# Add analysis_history relationship to User
User.analysis_history = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")

# Buying Recommendations
class BuyingRecommendation(Base):
    __tablename__ = "buying_recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False)  # 'high', 'medium', 'low'
    reason = Column(Text, nullable=False)
    estimated_price = Column(String(50), nullable=True)
    style_match = Column(Float, nullable=True)  # Percentage match
    color_suggestions = Column(JSON, nullable=True)  # List of suggested colors
    created_at = Column(DateTime, server_default=func.now())
    is_purchased = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="buying_recommendations")

# Add buying_recommendations relationship to User
User.buying_recommendations = relationship("BuyingRecommendation", back_populates="user", cascade="all, delete-orphan")

# Weather Cache (for performance)
class WeatherCache(Base):
    __tablename__ = "weather_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    weather_data = Column(JSON, nullable=False)
    cached_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)

# Image Processing Cache
class ImageProcessingCache(Base):
    __tablename__ = "image_processing_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    image_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash
    processing_result = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
# User preferences for AI recommendations
class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    preferred_colors = Column(JSON, nullable=True)  # List of preferred colors
    preferred_styles = Column(JSON, nullable=True)  # List of preferred styles
    body_type = Column(String(50), nullable=True)
    size_preferences = Column(JSON, nullable=True)  # Size information
    budget_range = Column(JSON, nullable=True)  # Min/max budget
    style_personality = Column(String(100), nullable=True)  # 'minimalist', 'trendy', etc.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")

# Add preferences relationship to User
User.preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")