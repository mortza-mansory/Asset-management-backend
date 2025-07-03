from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.features.assets_loan_management.data.repository import LoanRepository
from app.features.assets_loan_management.data.schemas import AssetLoanCreate, AssetLoanResponse
from app.features.assets_loan_management.service.loan_service import LoanService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/assets/loans", tags=["assets_loans"])
limiter = Limiter(key_func=get_remote_address)

def get_loan_service(db: Session = Depends(get_db)) -> LoanService:
    repository = LoanRepository(db)
    return LoanService(repository, db)

@router.post("/", response_model=AssetLoanResponse)
@limiter.limit("5/minute")
async def create_loan(
    request: Request,
    loan: AssetLoanCreate,
    loan_service: LoanService = Depends(get_loan_service),
    current_user: dict = Depends(get_current_user)
):
    return loan_service.create_loan(loan, current_user)

@router.post("/{loan_id}/return", response_model=AssetLoanResponse)
@limiter.limit("5/minute")
async def return_loan(
    request: Request,
    loan_id: int,
    loan_service: LoanService = Depends(get_loan_service),
    current_user: dict = Depends(get_current_user)
):
    return loan_service.return_loan(loan_id, current_user)