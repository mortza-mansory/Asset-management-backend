from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.features.assets_management.data.models import AssetStatus, AssetEventType

class AssetCategoryCreate(BaseModel):
    name: str  # e.g., تجهیزات الکترونیکی
    code: int  # e.g., 100
    description: Optional[str] = None

class AssetCategoryResponse(BaseModel):
    id: int
    name: str
    code: int
    description: Optional[str]

    class Config:
        from_attributes = True

class AssetCreate(BaseModel):
    company_id: int
    asset_id: str  # e.g., P-58290
    category_id: int  # e.g., ID دسته‌بندی لپ‌تاپ
    name: str  # e.g., لپ‌تاپ Dell XPS 15
    rfid_tag: str  # e.g., E28011700000020B02B5095C
    model: Optional[str] = None
    serial_number: Optional[str] = None
    technical_specs: Optional[str] = None
    location: Optional[str] = None
    custodian: Optional[str] = None
    value: Optional[int] = None
    registration_date: Optional[datetime] = None
    warranty_end_date: Optional[datetime] = None
    description: Optional[str] = None
    status: AssetStatus = AssetStatus.ACTIVE
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geofence_radius: Optional[float] = None  # شعاع محدوده (متر)

class AssetResponse(BaseModel):
    id: int
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

    class Config:
        from_attributes = True

class AssetLoanCreate(BaseModel):
    asset_id: int
    recipient_id: Optional[int] = None  # کاربر داخل شرکت
    external_recipient: Optional[str] = None  # گیرنده خارجی
    end_date: Optional[datetime] = None
    details: Optional[str] = None

class AssetLoanResponse(BaseModel):
    id: int
    asset_id: int
    recipient_id: Optional[int]
    external_recipient: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    details: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True