from fastapi import HTTPException, status
from app.features.work_flow.data.repository import WorkFlowRepository
from app.features.work_flow.data.schemas import WorkFlowResponse
from app.features.work_flow.data.models import WorkflowActionType
from app.features.logs.data.models import Log
from datetime import datetime
from typing import List, Optional

class WorkFlowService:
    def __init__(self, repository: WorkFlowRepository):
        self.repository = repository
        self.db = repository.db

    def list_workflows(
        self,
        company_id: int,
        current_user: dict,
        page: int,
        per_page: int,
        action_type: Optional[WorkflowActionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WorkFlowResponse]:
        if current_user["role"] not in ["S", "A1", "A2"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access workflows")
        
        if current_user["role"] != "S" and current_user.get("company_id") != company_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access workflows of your own company")
        
        workflows = self.repository.get_workflows(company_id, page, per_page, action_type, start_date, end_date)
        self._log_action(
            user_id=current_user["id"],
            action="WORKFLOW_ACCESS",
            entity_type="WORKFLOW",
            entity_id=company_id,
            details=f"Accessed workflows for company {company_id}"
        )
        return [WorkFlowResponse.from_orm(workflow) for workflow in workflows]

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