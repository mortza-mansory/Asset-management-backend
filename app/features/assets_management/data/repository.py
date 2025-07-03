from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.assets_management.data.models import Asset, AssetCategory, AssetStatusHistory
from app.features.assets_management.data.schemas import AssetCreate, AssetCategoryCreate
from app.core.models.company import Company
from typing import Optional, List

class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category: AssetCategoryCreate) -> AssetCategory:
        db_category = AssetCategory(
            name=category.name,
            code=category.code,
            description=category.description
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def create_asset(self, asset: AssetCreate, user_id: int) -> Asset:
        if not self.db.query(Company).filter(Company.id == asset.company_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        if not self.db.query(AssetCategory).filter(AssetCategory.id == asset.category_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
        db_asset = Asset(
            company_id=asset.company_id,
            asset_id=asset.asset_id,
            category_id=asset.category_id,
            name=asset.name,
            rfid_tag=asset.rfid_tag,
            model=asset.model,
            serial_number=asset.serial_number,
            technical_specs=asset.technical_specs,
            location=asset.location,
            custodian=asset.custodian,
            value=asset.value,
            registration_date=asset.registration_date,
            warranty_end_date=asset.warranty_end_date,
            description=asset.description,
            status=asset.status
        )
        self.db.add(db_asset)
        self.db.commit()
        self.db.refresh(db_asset)

        status_history = AssetStatusHistory(
            asset_id=db_asset.id,
            location=asset.location,
            status=asset.status,
            event_type="registered",
            user_id=user_id,
            details=f"Asset {asset.name} registered"
        )
        self.db.add(status_history)
        self.db.commit()
        return db_asset

    def get_asset_by_rfid(self, rfid_tag: str) -> Optional[Asset]:
        return self.db.query(Asset).filter(Asset.rfid_tag == rfid_tag).first()

    def get_assets_by_company(self, company_id: int, page: int, per_page: int) -> List[Asset]:
        offset = (page - 1) * per_page
        return self.db.query(Asset).filter(Asset.company_id == company_id).offset(offset).limit(per_page).all()