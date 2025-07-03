from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.features.assets_report_management.data.repository import ReportRepository
from app.features.assets_report_management.data.schemas import AssetReportResponse
from app.features.assets_report_management.service.report_service import ReportService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/assets/reports", tags=["assets_reports"])
limiter = Limiter(key_func=get_remote_address)

def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    repository = ReportRepository(db)
    return ReportService(repository)

@router.get("/company/{company_id}", response_model=AssetReportResponse)
@limiter.limit("5/minute")
async def get_company_report(
    request: Request,
    company_id: int,
    report_service: ReportService = Depends(get_report_service),
    current_user: dict = Depends(get_current_user)
):
    return report_service.get_company_report(company_id, current_user)