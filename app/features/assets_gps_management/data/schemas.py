from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AssetLocationCreate(BaseModel):
    asset_id: int
    latitude: float
    longitude: float
    geofence_radius: Optional[float] = None

class AssetLocationResponse(BaseModel):
    id: int
    asset_id: int
    latitude: float
    longitude: float
    geofence_radius: Optional[float]
    updated_at: datetime

    class Config:
        from_attributes = True

class GeofenceCheck(BaseModel):
    latitude: float
    longitude: float