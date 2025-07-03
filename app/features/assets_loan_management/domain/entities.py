from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AssetLoanEntity:
    id: Optional[int]
    asset_id: int
    company_id: int
    recipient_id: Optional[int]
    external_recipient: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    details: Optional[str]
    is_active: bool
    created_at: datetime