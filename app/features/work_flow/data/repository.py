from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.features.work_flow.data.models import WorkFlow, WorkflowActionType
from app.features.assets_management.data.models import Asset
from app.features.auth.data.models import User, UserCompanyRole
from app.core.models.company import Company
from typing import List, Optional
from datetime import datetime

class WorkFlowRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_workflows(
        self,
        company_id: int,
        page: int,
        per_page: int,
        action_type: Optional[WorkflowActionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[WorkFlow]:
        query = self.db.query(WorkFlow).filter(WorkFlow.company_id == company_id)
        
        if action_type:
            query = query.filter(WorkFlow.action_type == action_type)
        
        if start_date and end_date:
            query = query.filter(and_(
                WorkFlow.timestamp >= start_date,
                WorkFlow.timestamp <= end_date
            ))
        
        offset = (page - 1) * per_page
        return query.order_by(WorkFlow.timestamp.desc()).offset(offset).limit(per_page).all()

    def create_workflow(self, company_id: int, user_id: int, asset_id: int, action_type: WorkflowActionType, details: Optional[str] = None, is_offline: bool = False, is_actionable: bool = False) -> WorkFlow:
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not self.db.query(Company).filter(Company.id == company_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        # بررسی دسترسی کاربر به شرکت
        user_role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.company_id == company_id
        ).first()
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not associated with this company")
        
        workflow = WorkFlow(
            company_id=company_id,
            user_id=user_id,
            admin_name=user.username,
            asset_id=asset_id,
            asset_name=asset.name,
            action_type=action_type,
            details=details,
            is_offline=is_offline,
            is_actionable=is_actionable
        )
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow