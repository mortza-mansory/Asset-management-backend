from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.security import get_current_user, oauth2_scheme, SECRET_KEY, ALGORITHM
from app.features.auth.data.models import User, LoginAttempt
from app.features.auth.service.auth_service import AuthService
from app.features.auth.data.schemas import (
    LoginAttemptResponse, UserCreate, UserResponse, VerifyOtpRequest, SignUpResponse, LoginResponse, ResetCodeResponse
)
from app.db import get_db
from typing import Dict
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/signup", response_model=SignUpResponse)
async def signup(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.signup(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=LoginResponse)
async def login(username: str, password: str, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.login(username, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/verify-login-otp", response_model=dict)
async def verify_login_otp(request: VerifyOtpRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        token = auth_service.verify_login_otp(request)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/reset-password", response_model=ResetCodeResponse)
async def reset_password(identifier: str, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.request_reset_code(identifier)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/verify-reset-code")
async def verify_reset_code(user_id: int, code: str, new_password: str, auth_service: AuthService = Depends(get_auth_service)):
    try:
        auth_service.verify_reset_code(user_id, code, new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/verify-token", response_model=Dict)
async def verify_token(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing 'username' in token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User with username {username} not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        client_ip = request.client.host
        attempt_count = db.query(LoginAttempt).filter(
            LoginAttempt.ip_address == client_ip,
            LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=30)
        ).count()

        if attempt_count >= 10:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many attempts. IP banned for 5 hours."
            )

        role = user.companies[0].role if user.companies else None
        is_premium = auth_service.verify_premium_status(user.id)

        return {
            "valid": True,
            "payload": payload,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_num": user.phone_num,
                "is_active": user.is_active,
                "is_premium": is_premium,
                "role": role
            }
        }
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/premium-status", response_model=dict)
async def get_premium_status(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    is_premium = auth_service.verify_premium_status(current_user["id"])
    return {"is_premium": is_premium}