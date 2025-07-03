from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.features.work_flow.data.models import WorkflowActionType

@dataclass
class WorkFlowEntity:
    id: Optional[int]
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