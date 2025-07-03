from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CompanyEntity:
    id: Optional[int]
    name: str
    government_admin_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class UserEntity:
    id: Optional[int]
    username: str
    phone_num: Optional[str]
    email: Optional[str]
    hashed_password: str
    role: str
    company_id: Optional[int]
    is_active: bool
    can_delete_government: Optional[bool] = False
    can_manage_government_admins: Optional[bool] = False
    can_manage_operators: Optional[bool] = False