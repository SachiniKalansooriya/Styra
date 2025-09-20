# app/models/favorite_outfit.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class FavoriteOutfit(Base):
    __tablename__ = 'favorite_outfits'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    outfit_name = Column(String(255), nullable=False)
    outfit_data = Column(Text, nullable=False)  # JSON string of outfit items
    occasion = Column(String(100))
    season = Column(String(50))
    weather_context = Column(Text)  # JSON string of weather data when saved
    confidence_score = Column(Integer, default=0)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    times_worn = Column(Integer, default=0)
    last_worn = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FavoriteOutfit(id={self.id}, name='{self.outfit_name}', user_id={self.user_id})>"
