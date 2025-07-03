from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.features.auth.data.repository import SQLAlchemyUserRepository 
from app.features.subscription.api.routes import get_subscription_service
from app.features.subscription.service.subscription_service import SubscriptionService
from app.features.users.data.schemas import UserCreate, UserProfileResponse, UserUpdate, UserResponse
from app.features.users.service.user_service import UserService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, List

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

def get_user_service(
    db: Session = Depends(get_db),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
) -> UserService:
    repository = SQLAlchemyUserRepository(db) 
    return UserService(repository=repository, subscription_service=subscription_service)


@router.post("/", response_model=UserResponse)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return user_service.create_user(
        user.username,
        user.phone_num,
        user.email,
        user.password,
        user.role,
        user.company_id,
        user.can_delete_government,
        user.can_manage_government_admins,
        user.can_manage_operators,
        current_user
    )

@router.get("/me", response_model=UserProfileResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_current_user_profile(current_user)
    
@router.put("/{user_id}", response_model=UserResponse)
@limiter.limit("5/minute")
async def update_user(
    request: Request,
    user_id: int,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return user_service.update_user(
        user_id,
        user.username,
        user.phone_num,
        user.email,
        user.password,
        user.role,
        user.company_id,
        user.is_active,
        user.can_delete_government,
        user.can_manage_government_admins,
        user.can_manage_operators,
        current_user
    )

@router.delete("/{user_id}")
@limiter.limit("5/minute")
async def delete_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    user_service.delete_user(user_id, current_user)
    return {"message": "User deleted successfully"}

@router.get("/", response_model=List[UserResponse])
async def list_users(
    company_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return user_service.list_users(
        company_id=company_id,
        current_user=current_user,
        page=page,
        per_page=per_page
    )

@router.post("/{user_id}/change-role", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    new_role: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    return user_service.change_user_role(
        user_id=user_id,
        new_role=new_role,
        current_user=current_user
    )