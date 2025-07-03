from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from datetime import datetime
from app.core.models.base import Base

class AssetLocation(Base):
    __tablename__ = "asset_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    geofence_radius = Column(Float, nullable=True)  # شعاع محدوده (متر)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)