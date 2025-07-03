from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.features.assets_management.data.repository import AssetRepository
from app.features.assets_management.data.schemas import AssetCreate, AssetResponse, AssetCategoryCreate, AssetCategoryResponse
from app.features.assets_management.service.asset_service import AssetService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

router = APIRouter(prefix="/assets", tags=["assets"])
limiter = Limiter(key_func=get_remote_address)

def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    repository = AssetRepository(db)
    return AssetService(repository)

@router.post("/categories", response_model=AssetCategoryResponse)
@limiter.limit("5/minute")
async def create_category(
    request: Request,
    category: AssetCategoryCreate,
    asset_service: AssetService = Depends(get_asset_service),
    current_user: dict = Depends(get_current_user)
):
    return asset_service.create_category(category, current_user)

@router.post("/", response_model=AssetResponse)
@limiter.limit("5/minute")
async def create_asset(
    request: Request,
    asset: AssetCreate,
    asset_service: AssetService = Depends(get_asset_service),
    current_user: dict = Depends(get_current_user)
):
    return asset_service.create_asset(asset, current_user)

@router.get("/", response_model=List[AssetResponse])
@limiter.limit("5/minute")
async def list_assets(
    request: Request,
    company_id: int,
    page: int = 1,
    per_page: int = 20,
    asset_service: AssetService = Depends(get_asset_service),
    current_user: dict = Depends(get_current_user)
):
    return asset_service.list_assets(company_id, current_user, page, per_page)

@router.get("/rfid/{rfid_tag}", response_model=AssetResponse)
@limiter.limit("10/minute")
async def get_asset_by_rfid(
    request: Request,
    rfid_tag: str,
    asset_service: AssetService = Depends(get_asset_service),
    current_user: dict = Depends(get_current_user)
):
    return asset_service.get_asset_by_rfid(rfid_tag, current_user)