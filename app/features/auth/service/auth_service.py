from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.features.auth.data.models import User, OtpToken, ResetCode, LoginAttempt
from app.features.auth.data.schemas import UserCreate, UserResponse, VerifyOtpRequest, SignUpResponse, LoginResponse, ResetCodeResponse
from app.core.security import get_password_hash, verify_password, SECRET_KEY, ALGORITHM
from app.core.logger.logger import DatabaseLogger
from datetime import datetime, timedelta
import secrets
import jwt
from typing import Optional

from app.features.subscription.data.models import Subscription

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = DatabaseLogger(db)

    def signup(self, user: UserCreate) -> SignUpResponse:
        if self.db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        if user.email and self.db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        if user.phone_num and self.db.query(User).filter(User.phone_num == user.phone_num).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            phone_num=user.phone_num,
            email=user.email,
            hashed_password=hashed_password,
            is_active=False
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        self.logger.log(action="USER_SIGNUP", user_id=db_user.id, details=f"User {user.username} signed up")

        otp = secrets.token_hex(3)  # 6-character OTP
        temp_token_str = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        otp_token = OtpToken(
            user_id=db_user.id,
            identifier=user.email or user.phone_num or user.username,
            token=otp,
            temp_token=temp_token_str,
            used=False,
            expires_at=expires_at
        )
        self.db.add(otp_token)
        self.db.commit()

        print(f"Signup OTP for user {db_user.id}: {otp}")

        return SignUpResponse(
            id=db_user.id,
            username=db_user.username,
            phone_num=db_user.phone_num,
            email=db_user.email,
            is_active=db_user.is_active,
            temp_token=temp_token_str
        )

    def login(self, username: str, password: str) -> LoginResponse:
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            self.logger.log(action="LOGIN_FAILED", details=f"Failed login for {username}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")

        # Remove is_active check to allow OTP verification to activate the user
        otp = secrets.token_hex(3)
        temp_token_str = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        otp_token = OtpToken(
            user_id=user.id,
            identifier=username,
            token=otp,
            temp_token=temp_token_str,
            used=False,
            expires_at=expires_at
        )
        self.db.add(otp_token)
        self.db.commit()

        self.logger.log(action="LOGIN_ATTEMPT", user_id=user.id, details=f"Login OTP sent for {username}")

        print(f"Login OTP for user {user.id}: {otp}")

        return LoginResponse(
            message="Login OTP sent",
            user_id=user.id,
            temp_token=temp_token_str
        )

    def verify_login_otp(self, request: VerifyOtpRequest) -> str:
        otp_token = self.db.query(OtpToken).filter(
            OtpToken.user_id == request.user_id,
            OtpToken.token == request.otp,
            OtpToken.temp_token == request.temp_token,
            OtpToken.used == False,
            OtpToken.expires_at > datetime.utcnow()
        ).first()

        if not otp_token:
            print(f"OTP verification failed for user_id={request.user_id}, otp={request.otp}, temp_token={request.temp_token}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid, expired, or incorrect OTP/Session")

        user = self.db.query(User).filter(User.id == request.user_id).first()
        if not user:
            print(f"User not found for user_id={request.user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        otp_token.used = True
        if not user.is_active:
            user.is_active = True
            self.logger.log(action="USER_ACTIVATED", user_id=user.id, details=f"User {user.username} activated")
        
        self.db.commit()
        self.db.refresh(user)
        print(f"User {user.username} processed, is_active={user.is_active}")

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "is_premium": user.is_premium,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        self.logger.log(action="LOGIN_SUCCESS", user_id=user.id, details=f"User {user.username} logged in")

        return token

    def verify_premium_status(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        active_subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            Subscription.end_date > datetime.utcnow()
        ).first()
        if not active_subscription and user.is_premium:
            user.is_premium = False
            self.db.commit()
        return user.is_premium

    def request_reset_code(self, identifier: str) -> ResetCodeResponse:
        user = self.db.query(User).filter(
            (User.username == identifier) | (User.email == identifier) | (User.phone_num == identifier)
        ).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        code = secrets.token_hex(3)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        reset_code = ResetCode(user_id=user.id, code=code, is_used=False, expires_at=expires_at)
        self.db.add(reset_code)
        self.db.commit()

        self.logger.log(action="RESET_CODE_REQUEST", user_id=user.id, details=f"Reset code requested for {user.username}")

        print(f"Reset code for {user.username}: {code}")

        return ResetCodeResponse.from_orm(reset_code)

    def verify_reset_code(self, user_id: int, code: str, new_password: str):
        reset_code = self.db.query(ResetCode).filter(
            ResetCode.user_id == user_id,
            ResetCode.code == code,
            ResetCode.is_used == False,
            ResetCode.expires_at > datetime.utcnow()
        ).first()
        if not reset_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset code")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        reset_code.is_used = True
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()

        self.logger.log(action="PASSWORD_RESET", user_id=user_id, details=f"Password reset for {user.username}")