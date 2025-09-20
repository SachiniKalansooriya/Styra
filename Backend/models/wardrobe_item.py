from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..database.database import Base

class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    color = Column(String(30), nullable=False)
    brand = Column(String(100))
    size = Column(String(20))
    season = Column(String(20), default='All')
    formality_level = Column(String(30), default='Casual')
    image_url = Column(String(500))
    times_worn = Column(Integer, default=0, nullable=False)
    last_worn = Column(DateTime(timezone=True))
    is_available = Column(Boolean, default=True, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # No owner_id or user relationship for now