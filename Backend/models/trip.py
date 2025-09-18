# models/trip.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Trip(Base):
    __tablename__ = 'trips'
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)  # For now, default user
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)  # days
    activities = Column(JSON, nullable=True)  # List of activities
    weather_expected = Column(String(100), nullable=True)
    packing_style = Column(String(100), nullable=False, default='minimal')
    
    # Packing list data
    packing_list = Column(JSON, nullable=True)  # Generated packing recommendations
    wardrobe_matches = Column(JSON, nullable=True)  # Items from user's wardrobe
    coverage_analysis = Column(JSON, nullable=True)  # Wardrobe coverage stats
    
    # Trip status
    is_completed = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration': self.duration,
            'activities': self.activities or [],
            'weather_expected': self.weather_expected,
            'packing_style': self.packing_style,
            'packing_list': self.packing_list or [],
            'wardrobe_matches': self.wardrobe_matches or {},
            'coverage_analysis': self.coverage_analysis or {},
            'is_completed': self.is_completed,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'notes': self.notes
        }
