from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Enum, Boolean, Index
from datetime import datetime
from app.core.models.base import Base
import enum

class WorkflowActionType(enum.Enum):
    ADDED = "added"
    EDITED = "edited"
    TRANSFERRED = "transferred"
    STATUS_CHANGED = "status_changed"
    OFFLINE_SCAN = "offline_scan"

class WorkFlow(Base):
    __tablename__ = "work_flows"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    admin_name = Column(String)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    asset_name = Column(String)
    action_type = Column(Enum(WorkflowActionType)) 
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    is_offline = Column(Boolean, default=False)
    is_actionable = Column(Boolean, default=False)

    __table_args__ = (
        Index('ix_work_flows_company_timestamp', 'company_id', 'timestamp'),
        Index('ix_work_flows_action_type', 'action_type'),  
    )
