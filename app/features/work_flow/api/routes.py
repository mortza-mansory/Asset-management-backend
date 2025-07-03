from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.features.work_flow.data.repository import WorkFlowRepository
from app.features.work_flow.data.schemas import WorkFlowResponse
from app.features.work_flow.data.models import WorkflowActionType
from app.features.work_flow.service.work_flow_service import WorkFlowService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/workflows", tags=["workflows"])
limiter = Limiter(key_func=get_remote_address)

def get_workflow_service(db: Session = Depends(get_db)) -> WorkFlowService:
    repository = WorkFlowRepository(db)
    return WorkFlowService(repository)

@router.get("/", response_model=List[WorkFlowResponse])
@limiter.limit("5/minute")
async def list_workflows(
    request: Request,
    company_id: int,
    page: int = 1,
    per_page: int = 20,
    action_type: Optional[WorkflowActionType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    workflow_service: WorkFlowService = Depends(get_workflow_service),
    current_user: dict = Depends(get_current_user)
):
    return workflow_service.list_workflows(company_id, current_user, page, per_page, action_type, start_date, end_date)