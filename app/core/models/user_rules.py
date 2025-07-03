from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional

class Role(str, Enum):
    O = "GOVERNMENT_OPERATOR"
    A1 = "GOVERNMENT_OWNER"
    A2 = "GOVERNMENT_ADMIN"
    S = "SUPER_ADMIN"

class UserRules(BaseModel):
    role: str  # S, A1 (Owner), A2 (Non-Owner), O
    allowed_fields: Dict[str, List[str]]  # e.g., {"users": ["id", "username"], "assets": ["id", "name"]}
    editable_fields: Dict[str, List[str]]  # e.g., {"users": ["username"], "assets": ["status"]}
    max_records: Optional[int] = None  # Maximum records a user can fetch per request
    can_delete_government: Optional[bool] = False  # For A2: Can delete Government Admins
    can_manage_government_admins: Optional[bool] = False  # For A2: Can add/remove Government Admins
    can_manage_operators: Optional[bool] = False  # For A2: Can add/remove Operators
    company_id: Optional[int] = None  # Restrict access to specific company

    class Config:
        json_schema_extra = {
            "example": {
                "role": "A2",
                "allowed_fields": {
                    "users": ["id", "username", "phone_num", "email"],
                    "assets": ["id", "name", "location"]
                },
                "editable_fields": {
                    "users": ["username"],
                    "assets": ["location"]
                },
                "max_records": 100,
                "can_delete_government": True,
                "can_manage_government_admins": True,
                "can_manage_operators": True,
                "company_id": 1
            }
        }