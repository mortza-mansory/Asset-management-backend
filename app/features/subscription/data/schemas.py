from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionCreate(BaseModel):
    plan_type: str

class SubscriptionResponse(BaseModel):
    id: int
    payment_url: str
    status: str
    payment_id: str
    
    class Config:
        from_attributes = True

class ActiveSubscriptionResponse(BaseModel):
    plan_type: str
    end_date: datetime

    class Config:
        from_attributes = True