from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.features.logs.service.log_service import LogService
from app.features.logs.data.repository import LogRepository
from app.db import get_db
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/logs", tags=["logs"])

class LogCreate(BaseModel):
    user_id: Optional[int]
    company_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]

class LogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    company_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=LogResponse)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    service = LogService(LogRepository(db), db)
    return service.create_log(
        user_id=log.user_id,
        company_id=log.company_id,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        details=log.details
    )

@router.delete("/{log_id}")
def delete_log(log_id: int, current_user: dict = Depends(lambda: {"id": 1, "role": "S"}), db: Session = Depends(get_db)):
    service = LogService(LogRepository(db), db)
    service.delete_log(log_id, current_user)
    return {"message": "Log deleted successfully"}

@router.get("/", response_model=List[LogResponse])
def get_logs(
    company_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(lambda: {"id": 1, "role": "S"}),
    db: Session = Depends(get_db)
):
    service = LogService(LogRepository(db), db)
    return service.get_logs(company_id, current_user, page, per_page, start_date, end_date)