from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class UserEntity:
    id: Optional[int]
    username: str
    phone_num: Optional[str]
    email: Optional[str]
    hashed_password: str
    is_active: bool


@dataclass
class ResetCodeEntity:
    id: Optional[int]
    user_id: int
    code: str
    created_at: datetime
    expires_at: datetime