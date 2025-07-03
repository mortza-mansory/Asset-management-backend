import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.features.logs.data.models import Log
from app.db import get_db

class DatabaseLogger:
    def __init__(self, db: Session):
        self.db = db

    def log(self, action: str, user_id: Optional[int] = None, company_id: Optional[int] = None, entity_type: Optional[str] = None, entity_id: Optional[int] = None, details: Optional[str] = ""):
        try:
            log_entry = Log(
                user_id=user_id,
                company_id=company_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
                timestamp=datetime.utcnow()
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logging.error(f"Failed to log to database: {str(e)}")