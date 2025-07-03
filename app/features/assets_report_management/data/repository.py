from sqlalchemy.orm import Session
from sqlalchemy import func
from app.features.assets_management.data.models import Asset, AssetStatus
from app.features.logs.data.models import Log
from app.core.models.company import Company
from fastapi import HTTPException, status

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_company_report(self, company_id: int) -> dict:
        if not self.db.query(Company).filter(Company.id == company_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        total_assets = self.db.query(Asset).filter(Asset.company_id == company_id).count()
        active_assets = self.db.query(Asset).filter(Asset.company_id == company_id, Asset.status == AssetStatus.ACTIVE).count()
        loaned_assets = self.db.query(Asset).filter(Asset.company_id == company_id, Asset.status == AssetStatus.ON_LOAN).count()
        last_activity = self.db.query(Log).filter(Log.entity_type.in_(["ASSET", "ASSET_LOAN", "ASSET_LOCATION"]), Log.entity_id.in_(
            self.db.query(Asset.id).filter(Asset.company_id == company_id)
        )).order_by(Log.timestamp.desc()).first()
        
        return {
            "company_id": company_id,
            "total_assets": total_assets,
            "active_assets": active_assets,
            "loaned_assets": loaned_assets,
            "last_activity": last_activity.timestamp if last_activity else None
        }