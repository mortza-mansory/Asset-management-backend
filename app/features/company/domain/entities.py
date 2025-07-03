from datetime import datetime
from typing import Optional

class CompanyEntity:
    def __init__(
        self,
        id: Optional[int],
        name: str,
        is_active: bool,
        created_at: datetime,
        updated_at: datetime,
        role: Optional[str] = None 
    ):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.role = role