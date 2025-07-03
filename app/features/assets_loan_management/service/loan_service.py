from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.features.assets_loan_management.data.models import AssetLoan
from app.features.assets_loan_management.data.repository import LoanRepository
from app.features.assets_loan_management.data.schemas import AssetLoanCreate, AssetLoanResponse
from app.features.auth.data.models import UserCompanyRole
from app.features.logs.data.models import Log
from datetime import datetime

class LoanService:
    def __init__(self, repository: LoanRepository, db: Session):
        self.repository = repository
        self.db = db

    def create_loan(self, loan: AssetLoanCreate, current_user: dict) -> AssetLoanResponse:
        # بررسی دسترسی کاربر
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == loan.company_id
        ).first()
        if not role or role.role not in ["A1", "S"] or (role.role == "A1" and not role.can_manage_operators):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to create loan")

        db_loan = self.repository.create_loan(loan, current_user["id"])

        self._log_action(
            user_id=current_user["id"],
            company_id=loan.company_id,
            action="LOAN_CREATE",
            entity_type="ASSET_LOAN",
            entity_id=db_loan.id,
            details=f"Created loan for asset {loan.asset_id}"
        )

        return AssetLoanResponse(
            id=db_loan.id,
            asset_id=db_loan.asset_id,
            recipient_id=db_loan.recipient_id,
            external_recipient=db_loan.external_recipient,
            start_date=db_loan.start_date,
            end_date=db_loan.end_date,
            details=db_loan.details,
            is_active=db_loan.is_active,
            created_at=db_loan.created_at
        )

    def return_loan(self, loan_id: int, current_user: dict) -> AssetLoanResponse:
        loan = self.db.query(AssetLoan).filter(AssetLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == current_user["id"],
            UserCompanyRole.company_id == loan.company_id
        ).first()
        if not role or role.role not in ["A1", "S"] or (role.role == "A1" and not role.can_manage_operators):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to return loan")

        db_loan = self.repository.return_loan(loan_id, current_user["id"])

        self._log_action(
            user_id=current_user["id"],
            company_id=loan.company_id,
            action="LOAN_RETURN",
            entity_type="ASSET_LOAN",
            entity_id=loan_id,
            details=f"Returned loan {loan_id} for asset {db_loan.asset_id}"
        )

        return AssetLoanResponse(
            id=db_loan.id,
            asset_id=db_loan.asset_id,
            recipient_id=db_loan.recipient_id,
            external_recipient=db_loan.external_recipient,
            start_date=db_loan.start_date,
            end_date=db_loan.end_date,
            details=db_loan.details,
            is_active=db_loan.is_active,
            created_at=db_loan.created_at
        )

    def _log_action(self, user_id: int, company_id: int, action: str, entity_type: str, entity_id: int, details: str):
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