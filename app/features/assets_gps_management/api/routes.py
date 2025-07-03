from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.features.assets_gps_management.data.repository import GpsRepository
from app.features.assets_gps_management.data.schemas import AssetLocationCreate, AssetLocationResponse, GeofenceCheck
from app.features.assets_gps_management.service.gps_service import GpsService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/assets/gps", tags=["assets_gps"])
limiter = Limiter(key_func=get_remote_address)

def get_gps_service(db: Session = Depends(get_db)) -> GpsService:
    repository = GpsRepository(db)
    return GpsService(repository)

@router.post("/", response_model=AssetLocationResponse)
@limiter.limit("5/minute")
async def create_location(
    request: Request,
    location: AssetLocationCreate,
    gps_service: GpsService = Depends(get_gps_service),
    current_user: dict = Depends(get_current_user)
):
    return gps_service.create_location(location, current_user)

@router.post("/{asset_id}/check_geofence", response_model=dict)
@limiter.limit("10/minute")
async def check_geofence(
    request: Request,
    asset_id: int,
    current_location: GeofenceCheck,
    gps_service: GpsService = Depends(get_gps_service),
    current_user: dict = Depends(get_current_user)
):
    return gps_service.check_geofence(asset_id, current_location, current_user)