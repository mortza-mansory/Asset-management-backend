from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.models.user_rules import Role
from app.features.subscription.data.schemas import ActiveSubscriptionResponse


class CompanyBase(BaseModel):
    name: str
    is_active: bool = True

class CompanyCreate(CompanyBase):
    government_admin_id: Optional[int] = None

class CompanyUpdate(CompanyBase):
    government_admin_id: Optional[int] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    government_admin_id: Optional[int]
    role: Optional[str]  

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    phone_num: Optional[str] = None
    email: Optional[str] = None
    role: Role = Role.O
    company_id: Optional[int] = None
    is_active: bool = True
    can_delete_government: bool = False
    can_manage_government_admins: bool = False
    can_manage_operators: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone_num: Optional[str]
    is_active: bool
    subscription: Optional[ActiveSubscriptionResponse] = None

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True