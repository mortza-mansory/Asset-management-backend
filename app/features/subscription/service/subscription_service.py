from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.features.subscription.data.models import Subscription
from app.features.subscription.data.repository import SubscriptionRepository
from app.features.subscription.data.schemas import SubscriptionResponse
from app.features.logs.data.models import Log
from app.features.auth.data.models import User
from app.core.security import get_current_user
import uuid
import os
from jose import jwt

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = SubscriptionRepository(db)
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
        self.ALGORITHM = "HS256"

    def create_subscription(self, plan_type: str, user_id: int, current_user: dict) -> SubscriptionResponse:
        existing_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
        if existing_subscription:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has an active subscription")

        plans = {
            "6month": {"price": 3000000, "days": 180},
            "yearly": {"price": 6000000, "days": 365},
            "unlimited": {"price": 20000000, "days": 3650}
        }

        if plan_type not in plans:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan type")

        payment_id = str(uuid.uuid4())
        temp_token_payload = {
            "sub": str(user_id),
            "payment_id": payment_id,
            "exp": datetime.utcnow() + timedelta(minutes=10)
        }
        temp_token = jwt.encode(temp_token_payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        payment_url = f"{base_url}/subscriptions/pay/{payment_id}?token={temp_token}"

        subscription = Subscription(
            user_id=user_id,
            plan_type=plan_type,
            price=plans[plan_type]["price"],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=plans[plan_type]["days"]),
            status="pending",
            payment_url=payment_url,
            payment_id=payment_id
        )
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)

        self._log_action(
            user_id=current_user["id"],
            action="SUBSCRIPTION_CREATE",
            entity_type="SUBSCRIPTION",
            entity_id=subscription.id,
            details=f"Created {plan_type} subscription for user with id {user_id}"
        )
        return SubscriptionResponse(
            id=subscription.id,
            payment_url=subscription.payment_url,
            status=subscription.status,
            payment_id=subscription.payment_id
        )

    def verify_payment(self, payment_id: str) -> SubscriptionResponse:
        subscription = self.db.query(Subscription).filter(
            Subscription.payment_id == payment_id,
            Subscription.status == "pending"
        ).first()
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription or payment not found")

        subscription.status = "active"
        subscription.start_date = datetime.utcnow()
        subscription.end_date = subscription.start_date + timedelta(days=self.get_plan_duration(subscription.plan_type))
        
        # Update user to premium and link subscription
        user = self.db.query(User).filter(User.id == subscription.user_id).first()
        if user:
            user.is_premium = True
            user.subscription_id = subscription.id
            self.db.commit()
            self.db.refresh(user)

        self.db.commit()
        self.db.refresh(subscription)

        self._log_action(
            user_id=subscription.user_id,
            action="SUBSCRIPTION_ACTIVATED",
            entity_type="SUBSCRIPTION",
            entity_id=subscription.id,
            details=f"Activated {subscription.plan_type} subscription for user with id {subscription.user_id}"
        )
        return SubscriptionResponse(
            id=subscription.id,
            payment_url=subscription.payment_url,
            status=subscription.status,
            payment_id=subscription.payment_id
        )

    def get_plan_duration(self, plan_type: str) -> int:
        plans = {
            "6month": 180,
            "yearly": 365,
            "unlimited": 3650
        }
        return plans.get(plan_type, 30)

    def check_status(self, subscription_id: int, current_user: dict) -> bool:
        subscription = self.db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
        if not subscription:
            return False
        if current_user["role"] != "S" and subscription.user_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this subscription")
        return True

    def user_has_active_subscription(self, user_id: int) -> bool:
        active_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
        if not active_subscription:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and user.is_premium:
                user.is_premium = False
                self.db.commit()
            return False
        return True

    def user_can_create_company(self, user_id: int) -> bool:
        return self.user_has_active_subscription(user_id)

    def _log_action(self, user_id: int, action: str, entity_type: str, entity_id: int = None, details: str = ""):
        log = Log(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        
    def get_user_active_subscription_details(self, user_id: int) -> Optional[Subscription]:
        active_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
        return active_subscription