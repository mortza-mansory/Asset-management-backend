from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from app.core.models.user_rules import UserRules
from sqlalchemy.orm import Session
from app.features.auth.data.models import User, LoginAttempt
import os
from app.db import get_db
from fastapi import Depends, Request

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 4  
OTP_EXPIRE_MINUTES = 3  
MAX_LOGIN_ATTEMPTS = 10 
LOGIN_BAN_HOURS = 5  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:  
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username") 
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    client_ip = request.client.host
    attempt_count = db.query(LoginAttempt).filter(
        LoginAttempt.ip_address == client_ip,
        LoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=30)
    ).count()
    
    if attempt_count >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Too many attempts. IP banned for {LOGIN_BAN_HOURS} hours."
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    role = user.companies[0].role if user.companies else None
    company_id = user.companies[0].company_id if user.companies else None
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_num": user.phone_num,
        "is_active": user.is_active,
        "role": role,
        "company_id": company_id
    }

def get_user_rules(role: str, company_id: Optional[int] = None, permissions: Optional[dict] = None) -> UserRules:
    can_delete_government = permissions.get("can_delete_government", False) if permissions else False
    can_manage_government_admins = permissions.get("can_manage_government_admins", False) if permissions else False
    can_manage_operators = permissions.get("can_manage_operators", False) if permissions else False

    rules_map = {
        "S": UserRules(
            role="S",
            allowed_fields={
                "users": ["id", "username", "phone_num", "email", "role", "company_id", "is_active", "can_delete_government", "can_manage_government_admins", "can_manage_operators"],
                "companies": ["id", "name", "government_admin_id", "is_active"],
                "assets": ["id", "company_id", "name", "code", "location", "status", "rfid_tag", "gps_enabled", "geo_location"]
            },
            editable_fields={
                "users": ["username", "phone_num", "email", "role", "company_id", "is_active", "can_delete_government", "can_manage_government_admins", "can_manage_operators"],
                "companies": ["name", "government_admin_id", "is_active"],
                "assets": ["name", "code", "location", "status", "rfid_tag", "gps_enabled", "geo_location"]
            },
            max_records=None
        ),
        "A1": UserRules(
            role="A1",
            allowed_fields={
                "users": ["id", "username", "phone_num", "email", "role", "company_id", "is_active", "can_delete_government", "can_manage_government_admins", "can_manage_operators"],
                "assets": ["id", "name", "code", "location", "status", "rfid_tag", "gps_enabled", "geo_location"]
            },
            editable_fields={
                "users": ["username", "phone_num", "email", "role", "is_active", "can_delete_government", "can_manage_government_admins", "can_manage_operators"],
                "assets": ["name", "code", "location", "status", "rfid_tag", "gps_enabled", "geo_location"]
            },
            max_records=1000,
            company_id=company_id
        ),
        "A2": UserRules(
            role="A2",
            allowed_fields={
                "users": ["id", "username", "phone_num", "email", "role", "company_id", "is_active"],
                "assets": ["id", "name", "code", "location", "status"]
            },
            editable_fields={
                "users": ["username", "phone_num", "email", "is_active"] if can_manage_operators else [],
                "assets": ["location", "status"]
            },
            max_records=100,
            company_id=company_id,
            can_delete_government=can_delete_government,
            can_manage_government_admins=can_manage_government_admins,
            can_manage_operators=can_manage_operators
        ),
        "O": UserRules(
            role="O",
            allowed_fields={
                "assets": ["id", "name", "code", "location"]
            },
            editable_fields={},
            max_records=50,
            company_id=company_id
        )
    }
    return rules_map.get(role, rules_map["O"])