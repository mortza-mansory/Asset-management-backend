from sqlalchemy.orm import Session
from app.features.auth.data.models import User
from app.features.auth.data.schemas import UserCreate, UserResponse
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, List

class SQLAlchemyUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserResponse:
        db_user = User(
            username=user.username,
            phone_num=user.phone_num,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            phone_num=db_user.phone_num,
            email=db_user.email,
            is_active=db_user.is_active
        )

    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserResponse(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                is_active=db_user.is_active
            )
        return None

    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        db_user = self.db.query(User).filter(User.username == username).first()
        if db_user:
            return UserResponse(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                is_active=db_user.is_active
            )
        return None

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        db_user = self.db.query(User).filter(User.email == email).first()
        if db_user:
            return UserResponse(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                is_active=db_user.is_active
            )
        return None

    def get_user_by_phone_num(self, phone_num: str) -> Optional[UserResponse]:
        db_user = self.db.query(User).filter(User.phone_num == phone_num).first()
        if db_user:
            return UserResponse(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                is_active=db_user.is_active
            )
        return None

    def update_user(self, user: UserResponse) -> UserResponse:
        db_user = self.db.query(User).filter(User.id == user.id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        db_user.username = user.username
        db_user.phone_num = user.phone_num
        db_user.email = user.email
        if user.hashed_password:
            db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        self.db.commit()
        self.db.refresh(db_user)
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            phone_num=db_user.phone_num,
            email=db_user.email,
            is_active=db_user.is_active
        )

    def delete_user(self, user_id: int) -> None:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        db_user.is_active = False
        self.db.commit()