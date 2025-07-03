from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.features.logs.data.models import Log
from app.features.auth.data.models import UserCompanyRole
from typing import List, Optional
from datetime import datetime

class LogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_log(self, user_id: Optional[int], company_id: Optional[int], action: str, entity_type: str, entity_id: Optional[int], details: Optional[str]) -> Log:
        log = Log(
            user_id=user_id,
            company_id=company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def delete_log(self, log_id: int, current_user: dict) -> None:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"]
        ).first()
        if not role or role.role != "S":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins can delete logs")
        
        log = self.db.query(Log).filter(Log.id == log_id).first()
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
        
        self.db.delete(log)
        self.db.commit()

    def get_logs(self, company_id: Optional[int], page: int, per_page: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Log]:
        query = self.db.query(Log)
        if company_id:
            query = query.filter(Log.company_id == company_id)
        
        if start_date and end_date:
            query = query.filter(and_(
                Log.timestamp >= start_date,
                Log.timestamp <= end_date
            ))
        
        offset = (page - 1) * per_page
        return query.order_by(Log.timestamp.desc()).offset(offset).limit(per_page).all()