from fastapi import HTTPException, status
from app.features.assets_management.data.repository import AssetRepository
from app.features.assets_management.data.schemas import AssetCreate, AssetResponse, AssetCategoryCreate, AssetCategoryResponse
from app.features.assets_management.data.models import Asset
from app.features.auth.data.models import UserCompanyRole  # اضافه شده
from app.features.logs.data.models import Log
from app.features.work_flow.data.repository import WorkFlowRepository
from app.features.work_flow.data.models import WorkflowActionType
from datetime import datetime
from typing import List, Optional

class AssetService:
    def __init__(self, repository: AssetRepository):
        self.repository = repository
        self.db = repository.db
        self.workflow_repository = WorkFlowRepository(self.db)

    def create_category(self, category: AssetCategoryCreate, current_user: dict) -> AssetCategoryResponse:
        if current_user["role"] != "S":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins can create categories")
        
        db_category = self.repository.create_category(category)
        self._log_action(
            user_id=current_user["id"],
            action="CATEGORY_CREATE",
            entity_type="ASSET_CATEGORY",
            entity_id=db_category.id,
            details=f"Created category {category.name}"
        )
        return AssetCategoryResponse.from_orm(db_category)

    def create_asset(self, asset: AssetCreate, current_user: dict, company_id: int) -> AssetResponse:
        role = self._get_user_role(current_user["id"], company_id)
        if role not in ["S", "A1", "A2"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can create assets")
        
        db_asset = self.repository.create_asset(asset, current_user["id"])
        self._log_action(
            user_id=current_user["id"],
            company_id=company_id,
            action="ASSET_CREATE",
            entity_type="ASSET",
            entity_id=db_asset.id,
            details=f"Created asset {asset.name}"
        )
        self.workflow_repository.create_workflow(
            company_id=company_id,
            user_id=current_user["id"],
            asset_id=db_asset.id,
            asset_name=asset.name,
            action_type=WorkflowActionType.ADDED,
            details=f"Created asset {asset.name}"
        )
        return AssetResponse.from_orm(db_asset)

    def update_asset(self, asset_id: int, asset_update: dict, current_user: dict, company_id: int) -> AssetResponse:
        role = self._get_user_role(current_user["id"], company_id)
        if role not in ["S", "A1", "A2"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can update assets")
        
        asset = self.repository.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
        if asset.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update assets of your own company")
        
        action_type = WorkflowActionType.EDITED
        details = "Updated asset details"
        
        if asset_update.get("location") and asset_update["location"] != asset.location:
            action_type = WorkflowActionType.TRANSFERRED
            details = f"Transferred asset to {asset_update['location']}"
        elif asset_update.get("status") and asset_update["status"] != asset.status:
            action_type = WorkflowActionType.STATUS_CHANGED
            details = f"Changed status to {asset_update['status']}"
        
        for key, value in asset_update.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        asset.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(asset)
        
        self._log_action(
            user_id=current_user["id"],
            company_id=company_id,
            action="ASSET_UPDATE",
            entity_type="ASSET",
            entity_id=asset.id,
            details=details
        )
        self.workflow_repository.create_workflow(
            company_id=company_id,
            user_id=current_user["id"],
            asset_id=asset.id,
            asset_name=asset.name,
            action_type=action_type,
            details=details
        )
        return AssetResponse.from_orm(asset)

    def list_assets(self, company_id: int, current_user: dict, page: int, per_page: int) -> List[AssetResponse]:
        if current_user["role"] != "S" and current_user.get("company_id") != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view assets of your own company")
        
        assets = self.repository.get_assets_by_company(company_id, page, per_page)
        return [AssetResponse.from_orm(asset) for asset in assets]

    def get_asset_by_rfid(self, rfid_tag: str, current_user: dict) -> AssetResponse:
        asset = self.repository.get_asset_by_rfid(rfid_tag)
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
        if current_user["role"] != "S" and current_user.get("company_id") != asset.company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view assets of your own company")
        
        self._log_action(
            user_id=current_user["id"],
            action="ASSET_SCAN",
            entity_type="ASSET",
            entity_id=asset.id,
            details=f"Scanned RFID tag {rfid_tag}"
        )
        self.workflow_repository.create_workflow(
            company_id=asset.company_id,
            user_id=current_user["id"],
            asset_id=asset.id,
            asset_name=asset.name,
            action_type=WorkflowActionType.OFFLINE_SCAN,
            details=f"Scanned RFID tag {rfid_tag}",
            is_offline=True,
            is_actionable=True
        )
        return AssetResponse.from_orm(asset)

    def _get_user_role(self, user_id: int, company_id: int) -> str:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.company_id == company_id
        ).first()
        if not role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not associated with this company")
        return role.role

    def _log_action(self, user_id: int, company_id: int, action: str, entity_type: str, entity_id: int = None, details: str = ""):
        log = Log(
            user_id=user_id,
            company_id=company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()