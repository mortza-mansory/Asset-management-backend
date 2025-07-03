from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.models.base import Base
from app.core.models.company import Company


class UserCompanyRole(Base):
    __tablename__ = 'user_company_roles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    role = Column(String, nullable=False) # e.g., A1, A2, O

    #  فیلدهای جدید برای مدیریت عضویت
    status = Column(String, default="active", nullable=False)  # active, pending_invitation, pending_removal
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # دسترسی‌های فعلی
    can_manage_government_admins = Column(Boolean, default=False)
    can_manage_operators = Column(Boolean, default=False)
    can_delete_government = Column(Boolean, default=False)

    # روابط (relationships)
    user = relationship("User", back_populates="companies", foreign_keys=[user_id])
    company = relationship("Company", back_populates="users")
    
    #  رابطه جدید برای پیدا کردن دعوت‌کننده
    inviter = relationship("User", foreign_keys=[invited_by_id])
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    phone_num = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
   # companies = relationship("UserCompanyRole", back_populates="user")
    reset_codes = relationship("ResetCode", back_populates="user")
    companies = relationship("UserCompanyRole", back_populates="user", foreign_keys=[UserCompanyRole.user_id])


class OtpToken(Base):
    __tablename__ = "otp_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    identifier = Column(String, index=True)
    token = Column(String, index=True)
    temp_token = Column(String, index=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

class ResetCode(Base):
    __tablename__ = "reset_codes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    user = relationship("User", back_populates="reset_codes")

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False)
    username = Column(String, nullable=False)
    successful = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)