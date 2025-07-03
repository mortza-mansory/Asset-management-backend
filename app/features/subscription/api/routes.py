from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.features.subscription.data.models import Subscription
from app.features.subscription.data.schemas import SubscriptionCreate, SubscriptionResponse
from app.core.security import get_current_user
from app.db import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.features.subscription.service.subscription_service import SubscriptionService
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="app/templates/subscription")

def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    return SubscriptionService(db)

@router.post("/", response_model=SubscriptionResponse)
@limiter.limit("5/minute")
async def create_subscription(
    request: Request,
    data: SubscriptionCreate,
    service: SubscriptionService = Depends(get_subscription_service),
    current_user: dict = Depends(get_current_user)
):
    return service.create_subscription(
        plan_type=data.plan_type,
        user_id=current_user["id"],
        current_user=current_user
    )

@router.get("/{subscription_id}/status")
async def check_status(
    subscription_id: int,
    service: SubscriptionService = Depends(get_subscription_service),
    current_user: dict = Depends(get_current_user)
):
    return service.check_status(subscription_id, current_user)

@router.get("/status/me", response_model=dict)
async def get_my_subscription_status(
    request: Request,
    service: SubscriptionService = Depends(get_subscription_service),
    current_user: dict = Depends(get_current_user)
):
    has_active_sub = service.user_has_active_subscription(user_id=current_user["id"])
    return {"has_active_subscription": has_active_sub}

@router.get("/pay/{payment_id}", response_class=HTMLResponse)
async def get_payment_page(request: Request, payment_id: str, token: str = None, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.payment_id == payment_id).first()
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    try:
        secret_key = os.getenv("SECRET_KEY", "your-secret-key")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id or payload.get("payment_id") != payment_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        from app.features.auth.data.models import User
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return templates.TemplateResponse("index_fa.html", {
            "request": request,
            "plan_type": subscription.plan_type,
            "user_id": user_id,
            "payment_id": payment_id,
            "token": token  
        })
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.get("/verify-payment/{payment_id}", response_model=SubscriptionResponse)
async def verify_payment(
    payment_id: str,
    request: Request,
    service: SubscriptionService = Depends(get_subscription_service),
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    
    token = auth_header.replace("Bearer ", "")
    try:
        secret_key = os.getenv("SECRET_KEY", "your-secret-key")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id or payload.get("payment_id") != payment_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        from app.features.auth.data.models import User
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return service.verify_payment(payment_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")