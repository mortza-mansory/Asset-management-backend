from app.core.validators.role_validator import RoleValidator
from app.db import get_db
from app.features.company.domain.entities import CompanyEntity
from app.features.company.data.repository import CompanyRepository
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

class CreateCompanyUseCase:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def execute(self, name: str, current_user: dict) -> CompanyEntity:
        role = RoleValidator.get_user_role(current_user)
        if role != "S":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins can create companies")
        
        if self.repository.get_company_by_name(name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company name already exists")
        
        company = CompanyEntity(
            id=None,
            name=name,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return self.repository.create_company(company)

class UpdateCompanyUseCase:
    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def execute(self, company_id: int, name: str, is_active: Optional[bool], current_user: dict) -> CompanyEntity:
        from app.features.auth.data.models import UserCompanyRole
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        role = db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == company_id
        ).first()
        if not role or role.role not in ["A1", "S"] or (role.role == "A1" and not role.can_manage_government_admins):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins or authorized Admins can update companies")
        
        company = self.company_repository.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        company.name = name or company.name
        company.is_active = is_active if is_active is not None else company.is_active
        company.updated_at = datetime.utcnow()
        return self.company_repository.update_company(company)

class DeleteCompanyUseCase:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def execute(self, company_id: int, current_user: dict) -> None:
        from app.features.auth.data.models import UserCompanyRole
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        role = db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == company_id
        ).first()
        if not role or (role.role != "S" and not role.can_delete_government):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins or authorized users can delete companies")
        
        if not self.repository.get_company_by_id(company_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        self.repository.delete_company(company_id)

class ListCompaniesUseCase:
    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    def execute(self, current_user: dict, page: int, per_page: int) -> List[CompanyEntity]:
        from app.features.auth.data.models import UserCompanyRole
        from sqlalchemy.orm import Session
        db = next(get_db())
        
        role = db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"]
        ).first()
        if not role or role.role != "S":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins can list companies")
        
        companies = self.repository.get_companies(page, per_page)
        return companies