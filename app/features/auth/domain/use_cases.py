from app.features.auth.data.schemas import Role
from app.features.auth.domain.entities import UserEntity, ResetCodeEntity
from app.features.auth.domain.repositories import UserRepository
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.email.email import send_reset_code
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
import random
import string

from app.features.users.domain.entities import CompanyEntity

class LoginUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, password: str) -> dict:
        user = self.repository.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        access_token = create_access_token(data={"sub": user.username, "role": user.role, "id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

class SignupUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, username: str, phone_num: Optional[str], email: Optional[str], password: str, company_name: str) -> UserEntity:
        if not email and not phone_num:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one of email or phone number must be provided")
        if self.repository.get_user_by_username(username) or (email and self.repository.get_user_by_email(email)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
        if self.repository.get_company_by_name(company_name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company name already exists")
        
        company = self.repository.create_company(
            CompanyEntity(
                id=None,
                name=company_name,
                government_admin_id=None,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        
        hashed_password = get_password_hash(password)
        user = UserEntity(
            id=None,
            username=username,
            phone_num=phone_num,
            email=email,
            hashed_password=hashed_password,
            role=Role.A1,
            company_id=company.id,
            is_active=True
        )
        user = self.repository.create_user(user)
        
        company.government_admin_id = user.id
        self.repository.update_company(company)
        
        return user

class ForgotPasswordUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, email: Optional[str], phone_num: Optional[str]) -> str:
        if not email and not phone_num:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one of email or phone number must be provided")
        
        user = self.repository.get_user_by_email(email) if email else None
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        reset_code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=3)
        
        reset_code_entity = ResetCodeEntity(
            id=None,
            user_id=user.id,
            code=reset_code,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        self.repository.create_reset_code(reset_code_entity)
        
        if email:
            success = send_reset_code(email, reset_code)
            if not success:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send reset code")
        
        return reset_code

class ResetPasswordUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, reset_code: str, new_password: str) -> None:
        reset_code_entity = self.repository.get_reset_code(reset_code)
        if not reset_code_entity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset code")
        
        if datetime.utcnow() > reset_code_entity.expires_at:
            self.repository.delete_reset_code(reset_code)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expired reset code")
        
        user = self.repository.get_user_by_id(reset_code_entity.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user.hashed_password = get_password_hash(new_password)
        self.repository.update_user(user)
        
        self.repository.delete_reset_code(reset_code)