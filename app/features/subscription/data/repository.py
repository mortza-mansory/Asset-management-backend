from sqlalchemy.orm import Session
from app.features.subscription.data.models import Subscription
from typing import Optional

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_subscription(self, subscription: Subscription) -> Subscription:
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_subscription_by_company_id(self, company_id: int) -> Optional[Subscription]:
        return self.db.query(Subscription).filter(Subscription.company_id == company_id).first()