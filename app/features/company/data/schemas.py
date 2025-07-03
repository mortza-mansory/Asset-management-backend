from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    is_active: bool = True

class CompanyCreate(CompanyBase):
    government_admin_id: Optional[int] = None

class CompanyUpdate(CompanyBase):
    government_admin_id: Optional[int] = None

class CompanyResponse(CompanyBase):
    id: int
    government_admin_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    role: Optional[str] = None 

    class Config:
        from_attributes = True

class CompanyWithRoleResponse(BaseModel):
    id: int
    name: str
    role: str

    class Config:
        from_attributes = True

class CompanyOverviewResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    user_count: int
    assets_count: int
    
    class Config:
        from_attributes = True