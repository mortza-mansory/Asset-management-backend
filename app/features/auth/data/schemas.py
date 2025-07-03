import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    phone_num: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    phone_num: Optional[str]
    email: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class OtpTokenCreate(BaseModel):
    user_id: Optional[int]
    identifier: str
    token: str
    expires_at: int

class OtpTokenResponse(BaseModel):
    id: int
    user_id: Optional[int]
    identifier: str
    token: str
    created_at: int
    expires_at: int
    used: bool

    class Config:
        from_attributes = True

class VerifyOtpRequest(BaseModel):
    user_id: int
    otp: str
    temp_token: str

class ResetCodeCreate(BaseModel):
    user_id: int
    code: str
    expires_at: int

class ResetCodeResponse(BaseModel):
    id: int
    user_id: int
    code: str
    created_at: datetime.datetime
    expires_at: datetime.datetime 
    is_used: bool

    class Config:
        from_attributes = True

class LoginAttemptResponse(BaseModel):
    id: int
    ip_address: str
    username: str
    successful: bool
    timestamp: int

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    message: str
    user_id: int
    temp_token: str

class SignUpResponse(UserResponse):
    temp_token: str