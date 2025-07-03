from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException, status
from app.features.auth.data.models import User
from app.features.subscription.data.models import Subscription
from app.features.subscription.data.repository import SubscriptionRepository
from app.core.models.company import Company
from typing import Optional

class CreateSubscriptionUseCase:
    def __init__(self, repository: SubscriptionRepository):
        self.repository = repository

    def execute(self, company_id: int, plan_type: str, user_id: int, current_user: dict) -> Subscription:
        if current_user["role"] not in ["S", "A1"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins or Owners can create subscriptions")
        
        company = self.repository.db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        existing_subscription = self.repository.get_subscription_by_company_id(company_id)
        if existing_subscription and existing_subscription.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company already has an active subscription")
        
        plans = {
            "6month": {"price": 3000000, "days": 180},
            "yearly": {"price": 6000000, "days": 365},
            "unlimited": {"price": 20000000, "days": 3650}
        }
        
        if plan_type not in plans:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan type")
        
        subscription = Subscription(
            company_id=company_id,
            plan_type=plan_type,
            price=plans[plan_type]["price"],
            status="pending",
            payment_id=str(uuid.uuid4()),
            payment_url=f"https://payment.example.com/subscribe/{uuid.uuid4()}",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=plans[plan_type]["days"]),
            is_active=False
        )
        return self.repository.create_subscription(subscription)

class CheckSubscriptionStatusUseCase:
    def __init__(self, repository: SubscriptionRepository):
        self.repository = repository

    def execute(self, subscription_id: int, current_user: dict) -> dict:
        subscription = self.repository.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
        
        user_company = self.repository.db.query(User).filter(User.id == current_user["id"]).first().company_id
        if current_user["role"] not in ["S"] and subscription.company_id != user_company:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this subscription")
        
        return {
            "id": subscription.id,
            "company_id": subscription.company_id,
            "plan_type": subscription.plan_type,
            "status": subscription.status,
            "is_active": subscription.is_active,
            "expires_at": subscription.expires_at
        }
