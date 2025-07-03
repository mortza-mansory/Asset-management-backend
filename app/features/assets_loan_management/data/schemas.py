from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AssetLoanCreate(BaseModel):
    asset_id: int
    company_id: int
    recipient_id: Optional[int] = None
    external_recipient: Optional[str] = None
    end_date: Optional[datetime] = None
    details: Optional[str] = None

class AssetLoanResponse(BaseModel):
    id: int
    asset_id: int
    company_id: int
    recipient_id: Optional[int]
    external_recipient: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    details: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True