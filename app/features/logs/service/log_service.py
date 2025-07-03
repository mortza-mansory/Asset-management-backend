from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.features.logs.data.repository import LogRepository
from app.features.auth.data.models import UserCompanyRole
from typing import List, Optional
from datetime import datetime

class LogService:
    def __init__(self, repository: LogRepository, db: Session):
        self.repository = repository
        self.db = db

    def create_log(self, user_id: Optional[int], company_id: Optional[int], action: str, entity_type: str, entity_id: Optional[int], details: Optional[str]) -> dict:
        log = self.repository.create_log(user_id, company_id, action, entity_type, entity_id, details)
        return {
            "id": log.id,
            "user_id": log.user_id,
            "company_id": log.company_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "timestamp": log.timestamp
        }

    def delete_log(self, log_id: int, current_user: dict) -> None:
        self.repository.delete_log(log_id, current_user)

    def get_logs(self, company_id: Optional[int], current_user: dict, page: int, per_page: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"]
        ).first()
        if not role or role.role != "S":
            if company_id is None or not self.db.query(UserCompanyRole).filter(
                UserCompanyRole.user_id == current_user["id"],
                UserCompanyRole.company_id == company_id
            ).first():
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to view logs")
        
        logs = self.repository.get_logs(company_id, page, per_page, start_date, end_date)
        return [
            {
                "id": log.id,
                "user_id": log.user_id,
                "company_id": log.company_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "timestamp": log.timestamp
            }
            for log in logs
        ]