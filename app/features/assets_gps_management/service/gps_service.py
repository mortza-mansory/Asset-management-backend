from fastapi import HTTPException, status
from app.features.assets_gps_management.data.repository import GpsRepository
from app.features.assets_gps_management.data.schemas import AssetLocationCreate, AssetLocationResponse, GeofenceCheck
from app.features.assets_gps_management.domain.use_cases import CheckGeofenceUseCase
from app.features.logs.data.models import Log
from app.features.work_flow.data.repository import WorkFlowRepository
from app.features.work_flow.data.models import WorkflowActionType
from datetime import datetime
from app.features.assets_management.data.models import Asset

class GpsService:
    def __init__(self, repository: GpsRepository):
        self.repository = repository
        self.db = repository.db
        self.workflow_repository = WorkFlowRepository(self.db)

    def create_location(self, location: AssetLocationCreate, current_user: dict) -> AssetLocationResponse:
        if current_user["role"] not in ["S", "A1", "A2"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can create locations")
        
        db_location = self.repository.create_location(location)
        self._log_action(
            user_id=current_user["id"],
            action="LOCATION_CREATE",
            entity_type="ASSET_LOCATION",
            entity_id=db_location.id,
            details=f"Created location for asset {location.asset_id}"
        )
        asset = self.db.query(Asset).filter(Asset.id == location.asset_id).first()
        self.workflow_repository.create_workflow(
            company_id=asset.company_id,
            user_id=current_user["id"],
            asset_id=location.asset_id,
            asset_name=asset.name,
            action_type=WorkflowActionType.TRANSFERRED,
            details=f"Updated location to ({location.latitude}, {location.longitude})"
        )
        return AssetLocationResponse.from_orm(db_location)

    def check_geofence(self, asset_id: int, current_location: GeofenceCheck, current_user: dict) -> dict:
        if current_user["role"] not in ["S", "A1", "A2"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can check geofence")
        
        is_within_geofence = CheckGeofenceUseCase(self.repository).execute(
            asset_id, current_location.latitude, current_location.longitude
        )
        self._log_action(
            user_id=current_user["id"],
            action="GEOFENCE_CHECK",
            entity_type="ASSET_LOCATION",
            entity_id=asset_id,
            details=f"Checked geofence for asset {asset_id}: {'within' if is_within_geofence else 'outside'}"
        )
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        self.workflow_repository.create_workflow(
            company_id=asset.company_id,
            user_id=current_user["id"],
            asset_id=asset_id,
            asset_name=asset.name,
            action_type=WorkflowActionType.STATUS_CHANGED,
            details=f"Geofence check: {'within' if is_within_geofence else 'outside'} geofence"
        )
        return {"asset_id": asset_id, "is_within_geofence": is_within_geofence}

    def _log_action(self, user_id: int, action: str, entity_type: str, entity_id: int = None, details: str = ""):
        log = Log(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()