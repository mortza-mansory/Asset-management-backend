from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.features.work_flow.data.models import WorkflowActionType

class WorkFlowResponse(BaseModel):
    id: int
    company_id: int
    user_id: Optional[int]
    admin_name: str
    asset_id: int
    asset_name: str
    action_type: WorkflowActionType
    details: Optional[str]
    timestamp: datetime
    is_offline: bool
    is_actionable: bool

    class Config:
        from_attributes = True