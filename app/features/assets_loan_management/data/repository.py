import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.features.assets_management.data.models import Asset, AssetStatus, AssetStatusHistory
from app.features.assets_loan_management.data.models import AssetLoan
from app.features.assets_loan_management.data.schemas import AssetLoanCreate
from app.features.auth.data.models import User
from app.core.models.company import Company

class LoanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_loan(self, loan: AssetLoanCreate, user_id: int) -> AssetLoan:
        # بررسی وجود دارایی
        asset = self.db.query(Asset).filter(Asset.id == loan.asset_id).first()
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
        
        # بررسی وجود شرکت
        if not self.db.query(Company).filter(Company.id == loan.company_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        
        # بررسی وجود گیرنده (در صورت وجود)
        if loan.recipient_id and not self.db.query(User).filter(User.id == loan.recipient_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")
        
        # بررسی وجود گیرنده یا گیرنده خارجی
        if not loan.recipient_id and not loan.external_recipient:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either recipient_id or external_recipient must be provided")
        
        db_loan = AssetLoan(
            asset_id=loan.asset_id,
            company_id=loan.company_id,
            recipient_id=loan.recipient_id,
            external_recipient=loan.external_recipient,
            end_date=loan.end_date,
            details=loan.details
        )
        self.db.add(db_loan)
        
        # به‌روزرسانی وضعیت دارایی
        asset.status = AssetStatus.ON_LOAN
        self.db.add(asset)

        # ثبت تاریخچه وضعیت
        status_history = AssetStatusHistory(
            asset_id=loan.asset_id,
            status=AssetStatus.ON_LOAN,
            event_type="loaned",
            user_id=user_id,
            details=f"Asset loaned to {loan.external_recipient or loan.recipient_id}"
        )
        self.db.add(status_history)
        
        self.db.commit()
        self.db.refresh(db_loan)
        return db_loan

    def return_loan(self, loan_id: int, user_id: int) -> AssetLoan:
        loan = self.db.query(AssetLoan).filter(AssetLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        
        if not loan.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Loan already returned")
        
        loan.is_active = False
        loan.end_date = datetime.utcnow()
        
        # به‌روزرسانی وضعیت دارایی
        asset = self.db.query(Asset).filter(Asset.id == loan.asset_id).first()
        asset.status = AssetStatus.ACTIVE
        
        # ثبت تاریخچه وضعیت
        status_history = AssetStatusHistory(
            asset_id=loan.asset_id,
            status=AssetStatus.ACTIVE,
            event_type="returned",
            user_id=user_id,
            details=f"Asset returned from loan {loan_id}"
        )
        self.db.add(status_history)
        
        self.db.commit()
        self.db.refresh(loan)
        return loan