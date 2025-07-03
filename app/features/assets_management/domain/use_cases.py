from fastapi import HTTPException, status
from app.features.assets_management.data.repository import AssetRepository
from app.features.assets_management.data.schemas import AssetCreate, AssetCategoryCreate
from app.features.assets_management.data.models import Asset, AssetCategory
from app.core.models.company import Company
from typing import List

class CreateCategoryUseCase:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def execute(self, category: AssetCategoryCreate) -> AssetCategory:
        if self.repository.db.query(AssetCategory).filter(AssetCategory.code == category.code).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category code already exists")
        
        if self.repository.db.query(AssetCategory).filter(AssetCategory.name == category.name).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
        
        return self.repository.create_category(category)

class CreateAssetUseCase:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def execute(self, asset: AssetCreate, user_id: int) -> Asset:
        if self.repository.db.query(Asset).filter(Asset.asset_id == asset.asset_id).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset ID already exists")
        
        if self.repository.db.query(Asset).filter(Asset.rfid_tag == asset.rfid_tag).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RFID tag already exists")
        
        return self.repository.create_asset(asset, user_id)

class ListAssetsUseCase:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def execute(self, company_id: int, page: int, per_page: int) -> List[Asset]:
        if not self.repository.db.query(Company).filter(Company.id == company_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        return self.repository.get_assets_by_company(company_id, page, per_page)

class GetAssetByRfidUseCase:
    def __init__(self, repository: AssetRepository):
        self.repository = repository

    def execute(self, rfid_tag: str) -> Asset:
        asset = self.repository.get_asset_by_rfid(rfid_tag)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        return asset