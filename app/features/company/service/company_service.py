from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.models.company import Company
from app.features.company.domain.entities import CompanyEntity
from app.features.company.data.repository import CompanyRepository
from app.features.company.data.schemas import CompanyResponse
from app.features.auth.data.models import User, UserCompanyRole
from app.features.logs.data.models import Log
from app.features.subscription.service.subscription_service import SubscriptionService


class CompanyService:
    def __init__(self, repository: CompanyRepository, db: Session):
        self.repository = repository
        self.db = db
        self.subscription_service = SubscriptionService(db)

    def create_company(self, name: str, current_user: dict) -> CompanyResponse:
        if not self.subscription_service.user_has_active_subscription(current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Active subscription required to create a company")

        if self.repository.get_company_by_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Company name already exists")

        company_entity = CompanyEntity(
            id=None,
            name=name,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_company = self.repository.create_company(company_entity)

        user_company_role = UserCompanyRole(
            user_id=current_user["id"],
            company_id=db_company.id,
            role="A1",
            can_manage_government_admins=True,
            can_manage_operators=True,
            can_delete_government=True
        )
        self.db.add(user_company_role)
        self.db.commit()

        self._log_action(
            user_id=current_user["id"],
            company_id=db_company.id,
            action="COMPANY_CREATE",
            entity_type="COMPANY",
            entity_id=db_company.id,
            details=f"Created company {name}"
        )
        return CompanyResponse(
            id=db_company.id,
            name=db_company.name,
            is_active=db_company.is_active,
            created_at=db_company.created_at,
            updated_at=db_company.updated_at,
            government_admin_id=None,
            role="A1"
        )

    def update_company(self, company_id: int, name: str, government_admin_id: Optional[int], is_active: bool, current_user: dict) -> CompanyResponse:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == company_id
        ).first()
        if not role or role.role not in ["A1", "S"] or (role.role == "A1" and not role.can_manage_government_admins):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to update company")

        company = self.repository.get_company_by_id(company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        company.name = name or company.name
        company.is_active = is_active if is_active is not None else company.is_active
        company.updated_at = datetime.utcnow()
        db_company = self.repository.update_company(company)

        self._log_action(
            user_id=current_user["id"],
            company_id=company_id,
            action="COMPANY_UPDATE",
            entity_type="COMPANY",
            entity_id=company_id,
            details=f"Updated company {name or company.name}"
        )
        return CompanyResponse(
            id=db_company.id,
            name=db_company.name,
            is_active=db_company.is_active,
            created_at=db_company.created_at,
            updated_at=db_company.updated_at,
            government_admin_id=government_admin_id
        )

    def delete_company(self, company_id: int, current_user: dict) -> None:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == company_id
        ).first()

        is_super_admin = "S" in [r.role for r in self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"]).all()]

        if not (is_super_admin or (role and role.can_delete_government)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete company")

        self.repository.delete_company(company_id)
        self._log_action(
            user_id=current_user["id"],
            company_id=company_id,
            action="COMPANY_DELETE",
            entity_type="COMPANY",
            entity_id=company_id,
            details=f"Deleted company {company_id}"
        )

    def list_companies(self, current_user: dict, page: int, per_page: int) -> List[CompanyResponse]:
    
        user_id = current_user["id"]
        companies_data = self.repository.get_companies_for_user(
            user_id, page, per_page)

        response_list = []
        for company_data in companies_data:
            response_list.append(CompanyResponse(
                **company_data, government_admin_id=None))

        return response_list

    def who_is(self, current_user: dict) -> list:
        roles = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"]).all()
        return [
            {
                "company_id": role.company_id,
                "company_name": self.repository.get_company_by_id(role.company_id).name,
                "role": role.role,
                "can_delete_government": role.can_delete_government,
                "can_manage_government_admins": role.can_manage_government_admins,
                "can_manage_operators": role.can_manage_operators
            }
            for role in roles
        ]

    def _log_action(self, user_id: int, company_id: int, action: str, entity_type: str, entity_id: int = None, details: str = ""):
        log = Log(
            user_id=user_id,
            company_id=company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
    
    def get_company_overview(self, company_id: int, current_user: dict) -> dict:
        user_role_in_company = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == company_id
        ).first()

        if not user_role_in_company and current_user.get("role") != "S":
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        company = self.repository.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # تعداد کاربران شرکت را محاسبه می‌کنیم
        user_count = self.db.query(UserCompanyRole).filter(UserCompanyRole.company_id == company_id).count()
        
        # TODO: تعداد اموال در آینده محاسبه خواهد شد
        assets_count = 0 

        return {
            "id": company.id,
            "name": company.name,
            "is_active": company.is_active,
            "user_count": user_count,
            "assets_count": assets_count
        }