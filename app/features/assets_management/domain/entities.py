from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.features.assets_management.data.models import AssetStatus

@dataclass
class AssetEntity:
    id: Optional[int]
    company_id: int
    asset_id: str
    category_id: int
    name: str
    rfid_tag: str
    model: Optional[str]
    serial_number: Optional[str]
    technical_specs: Optional[str]
    location: Optional[str]
    custodian: Optional[str]
    value: Optional[int]
    registration_date: Optional[datetime]
    warranty_end_date: Optional[datetime]
    description: Optional[str]
    status: AssetStatus
    created_at: datetime
    updated_at: datetime

@dataclass
class AssetCategoryEntity:
    id: Optional[int]
    name: str
    code: int
    description: Optional[str]