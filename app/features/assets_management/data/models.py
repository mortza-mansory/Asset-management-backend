from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from datetime import datetime
from app.core.models.base import Base
import enum

class AssetStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DISPOSED = "disposed"
    ON_LOAN = "on_loan"

class AssetEventType(enum.Enum):
    SCANNED = "scanned"
    MOVED = "moved"
    ASSIGNED = "assigned"
    REGISTERED = "registered"
    LOANED = "loaned"
    RETURNED = "returned"

class AssetCategory(Base):
    __tablename__ = "asset_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # e.g., تجهیزات الکترونیکی
    code = Column(Integer, unique=True)  # e.g., 100 برای لپ‌تاپ
    description = Column(String, nullable=True)

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    asset_id = Column(String, unique=True, index=True)  # e.g., P-58290
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)  # اجباری
    name = Column(String)  # e.g., لپ‌تاپ Dell XPS 15
    rfid_tag = Column(String, unique=True, index=True)  # e.g., E28011700000020B02B5095C
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    technical_specs = Column(String, nullable=True)
    location = Column(String, nullable=True)
    custodian = Column(String, nullable=True)
    value = Column(Integer, nullable=True)
    registration_date = Column(DateTime, nullable=True)
    warranty_end_date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssetStatusHistory(Base):
    __tablename__ = "asset_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), index=True)
    location = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(AssetStatus))
    event_type = Column(Enum(AssetEventType))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    details = Column(String, nullable=True)