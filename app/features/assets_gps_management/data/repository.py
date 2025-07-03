from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.assets_management.data.models import Asset
from app.features.assets_gps_management.data.models import AssetLocation
from app.features.assets_gps_management.data.schemas import AssetLocationCreate
from typing import Optional

class GpsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_location(self, location: AssetLocationCreate) -> AssetLocation:
        if not self.db.query(Asset).filter(Asset.id == location.asset_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
        if self.db.query(AssetLocation).filter(AssetLocation.asset_id == location.asset_id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location already exists for this asset")
        
        db_location = AssetLocation(
            asset_id=location.asset_id,
            latitude=location.latitude,
            longitude=location.longitude,
            geofence_radius=location.geofence_radius
        )
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def get_location_by_asset_id(self, asset_id: int) -> Optional[AssetLocation]:
        return self.db.query(AssetLocation).filter(AssetLocation.asset_id == asset_id).first()