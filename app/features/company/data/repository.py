from sqlalchemy.orm import Session
from app.features.auth.data.models import UserCompanyRole
from app.features.company.domain.entities import CompanyEntity
from app.core.models.company import Company
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_company(self, company: CompanyEntity) -> CompanyEntity:
        db_company = Company(
            name=company.name,
            is_active=company.is_active
        )
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return CompanyEntity(
            id=db_company.id,
            name=db_company.name,
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
                is_active=db_company.is_active,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at
            )
        return None

    def get_companies_for_user(self, user_id: int, page: int, per_page: int) -> List[dict]:
 
        offset = (page - 1) * per_page
        results = (
            self.db.query(Company, UserCompanyRole.role)
            .join(UserCompanyRole, Company.id == UserCompanyRole.company_id)
            .filter(UserCompanyRole.user_id == user_id, Company.is_active == True)
            .offset(offset)
            .limit(per_page)
            .all()
        )
        companies_with_roles = []
        for company, role in results:
            companies_with_roles.append(
                {
                    "id": company.id,
                    "name": company.name,
                    "is_active": company.is_active,
                    "created_at": company.created_at,
                    "updated_at": company.updated_at,
                    "role": role,
                }
            )
        return companies_with_roles

    def update_company(self, company: CompanyEntity) -> CompanyEntity:
        db_company = self.db.query(Company).filter(Company.id == company.id).first()
        if not db_company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        db_company.name = company.name
        db_company.is_active = company.is_active
        db_company.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_company)
        return CompanyEntity(
            id=db_company.id,
            name=db_company.name,
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

    def get_company_by_id(self, company_id: int) -> Optional[CompanyEntity]:
        db_company = self.db.query(Company).filter(Company.id == company_id).first()
        if db_company:
            return CompanyEntity(
                id=db_company.id,
                name=db_company.name,
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
                is_active=db_company.is_active,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at
            )
        return None

    def get_companies(self, page: int, per_page: int) -> List[CompanyEntity]:
        offset = (page - 1) * per_page
        db_companies = self.db.query(Company).filter(Company.is_active == True).offset(offset).limit(per_page).all()
        return [
            CompanyEntity(
                id=db_company.id,
                name=db_company.name,
                is_active=db_company.is_active,
                created_at=db_company.created_at,
                updated_at=db_company.updated_at
            )
            for db_company in db_companies
        ]


    def get_companies_by_ids(self, company_ids: List[int], offset: int, limit: int) -> List[Company]:
     return self.db.query(Company).filter(
        Company.id.in_(company_ids),
        Company.is_active == True
    ).offset(offset).limit(limit).all()