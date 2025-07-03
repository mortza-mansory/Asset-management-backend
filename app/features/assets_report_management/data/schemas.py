from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AssetReportResponse(BaseModel):
    company_id: int
    total_assets: int
    active_assets: int
    loaned_assets: int
    last_activity: Optional[datetime]