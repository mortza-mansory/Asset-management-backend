from sqlalchemy.orm import Session
from app.features.auth.domain.entities import UserEntity, ResetCodeEntity
from app.features.users.domain.entities import CompanyEntity
from app.features.auth.domain.repositories import UserRepository
from app.features.auth.data.models import User, ResetCode
from app.core.models.company import Company
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, List

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserEntity) -> UserEntity:
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
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            phone_num=db_user.phone_num,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active
        )

    def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.username == username).first()
        if db_user:
            return UserEntity(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_premium=db_user.is_premium
            )
        return None

    def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.email == email).first()
        if db_user:
            return UserEntity(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_premium=db_user.is_premium
            )
        return None

    def create_reset_code(self, reset_code: ResetCodeEntity) -> ResetCodeEntity:
        db_reset_code = ResetCode(
            user_id=reset_code.user_id,
            code=reset_code.code,
            created_at=reset_code.created_at,
            expires_at=reset_code.expires_at
        )
        self.db.add(db_reset_code)
        self.db.commit()
        self.db.refresh(db_reset_code)
        return ResetCodeEntity(
            id=db_reset_code.id,
            user_id=db_reset_code.user_id,
            code=db_reset_code.code,
            created_at=db_reset_code.created_at,
            expires_at=db_reset_code.expires_at
        )

    def get_reset_code(self, code: str) -> Optional[ResetCodeEntity]:
        db_reset_code = self.db.query(ResetCode).filter(ResetCode.code == code).first()
        if db_reset_code:
            return ResetCodeEntity(
                id=db_reset_code.id,
                user_id=db_reset_code.user_id,
                code=db_reset_code.code,
                created_at=db_reset_code.created_at,
                expires_at=db_reset_code.expires_at
            )
        return None

    def delete_reset_code(self, code: str) -> None:
        db_reset_code = self.db.query(ResetCode).filter(ResetCode.code == code).first()
        if db_reset_code:
            self.db.delete(db_reset_code)
            self.db.commit()

    def create_company(self, company: CompanyEntity) -> CompanyEntity:
        db_company = Company(
            name=company.name,
            government_admin_id=company.government_admin_id,
            is_active=company.is_active
        )
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return CompanyEntity(
            id=db_company.id,
            name=db_company.name,
            government_admin_id=db_company.government_admin_id,
            is_active=db_company.is_active,
            created_at=db_company.created_at,
            updated_at=db_company.updated_at
        )

    def get_company_by_id(self, company_id: int) -> Optional[CompanyEntity]:
        db_company = self.db.query(Company).filter(Company.id == company_id).first()
        if db_company:
            return CompanyEntity(
                id=db_company.id,
                name=db_company.name,
                government_admin_id=db_company.government_admin_id,
                is_active=db_company.is_active,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at
            )
        return None

    def get_company_by_name(self, name: str) -> Optional[CompanyEntity]:
        db_company = self.db.query(Company).filter(Company.name == name).first()
        if db_company:
            return CompanyEntity(
                id=db_company.id,
                name=db_company.name,
                government_admin_id=db_company.government_admin_id,
                is_active=db_company.is_active,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at
            )
        return None

    def update_company(self, company: CompanyEntity) -> CompanyEntity:
        db_company = self.db.query(Company).filter(Company.id == company.id).first()
        if not db_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        db_company.name = company.name
        db_company.government_admin_id = company.government_admin_id
        db_company.is_active = company.is_active
        db_company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_company)
        return CompanyEntity(
            id=db_company.id,
            name=db_company.name,
            government_admin_id=db_company.government_admin_id,
            is_active=db_company.is_active,
            created_at=db_company.created_at,
            updated_at=db_company.updated_at
        )

    def delete_company(self, company_id: int) -> None:
        db_company = self.db.query(Company).filter(Company.id == company_id).first()
        if not db_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        db_company.is_active = False
        self.db.commit()

    def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            return UserEntity(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active
            )
        return None

    def update_user(self, user: UserEntity) -> UserEntity:
        db_user = self.db.query(User).filter(User.id == user.id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        db_user.username = user.username
        db_user.phone_num = user.phone_num
        db_user.email = user.email
        if user.hashed_password:
            db_user.hashed_password = user.hashed_password
        db_user.is_active = user.is_active
        db_user.is_premium = user.is_premium
        db_user.subscription_id = user.subscription_id
        self.db.commit()
        self.db.refresh(db_user)
        return UserEntity(
            id=db_user.id,
            username=db_user.username,
            phone_num=db_user.phone_num,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_premium=db_user.is_premium,
            subscription_id=db_user.subscription_id
        )

    def delete_user(self, user_id: int) -> None:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        db_user.is_active = False
        self.db.commit()

    def get_users_by_company(self, company_id: Optional[int]) -> List[UserEntity]:
        if company_id:
            db_users = self.db.query(User).filter(User.company_id == company_id).all()
        else:
            db_users = self.db.query(User).all()
        return [
            UserEntity(
                id=db_user.id,
                username=db_user.username,
                phone_num=db_user.phone_num,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_premium=db_user.is_premium,
                subscription_id=db_user.subscription_id
            )
            for db_user in db_users
        ]