from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean
from datetime import datetime
from app.core.models.base import Base

class AssetLoan(Base):
    __tablename__ = "asset_loans"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    external_recipient = Column(String, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    details = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)