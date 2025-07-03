from fastapi import HTTPException, status
from app.features.assets_report_management.data.repository import ReportRepository
from app.features.assets_report_management.data.schemas import AssetReportResponse
from app.features.logs.data.models import Log
from datetime import datetime

class ReportService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository
        self.db = repository.db

    def get_company_report(self, company_id: int, current_user: dict) -> AssetReportResponse:
        if current_user["role"] != "S":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins can access reports")
        
        report = self.repository.get_company_report(company_id)
        self._log_action(
            user_id=current_user["id"],
            action="REPORT_ACCESS",
            entity_type="REPORT",
            entity_id=company_id,
            details=f"Accessed report for company {company_id}"
        )
        return AssetReportResponse(**report)

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