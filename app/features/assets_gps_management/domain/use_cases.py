from fastapi import HTTPException, status
from app.features.assets_gps_management.data.repository import GpsRepository
from app.features.assets_gps_management.data.schemas import AssetLocationCreate
from app.features.assets_gps_management.data.models import AssetLocation
import math

class CreateLocationUseCase:
    def __init__(self, repository: GpsRepository):
        self.repository = repository

    def execute(self, location: AssetLocationCreate) -> AssetLocation:
        return self.repository.create_location(location)

class CheckGeofenceUseCase:
    def __init__(self, repository: GpsRepository):
        self.repository = repository

    def execute(self, asset_id: int, current_latitude: float, current_longitude: float) -> bool:
        location = self.repository.get_location_by_asset_id(asset_id)
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found for this asset")
        
        if not location.geofence_radius:
            return True  # محدوده‌ای تعریف نشده
        
        # محاسبه فاصله با فرمول Haversine
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # شعاع زمین (متر)
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        distance = haversine(location.latitude, location.longitude, current_latitude, current_longitude)
        return distance <= location.geofence_radius