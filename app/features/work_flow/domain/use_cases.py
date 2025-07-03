from fastapi import HTTPException, status
from app.features.work_flow.data.repository import WorkFlowRepository
from app.features.work_flow.data.models import WorkFlow, WorkflowActionType
from typing import List, Optional
from datetime import datetime

class ListWorkFlowsUseCase:
    def __init__(self, repository: WorkFlowRepository):
        self.repository = repository

    def execute(
        self,
        company_id: int,
        page: int,
        per_page: int,
        action_type: Optional[WorkflowActionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WorkFlow]:
        return self.repository.get_workflows(company_id, page, per_page, action_type, start_date, end_date)