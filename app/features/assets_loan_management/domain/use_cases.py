from fastapi import HTTPException, status
from app.features.assets_loan_management.data.repository import LoanRepository
from app.features.assets_loan_management.data.schemas import AssetLoanCreate
from app.features.assets_loan_management.data.models import AssetLoan

class CreateLoanUseCase:
    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def execute(self, loan: AssetLoanCreate, user_id: int) -> AssetLoan:
        return self.repository.create_loan(loan, user_id)

class ReturnLoanUseCase:
    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def execute(self, loan_id: int, user_id: int) -> AssetLoan:
        return self.repository.return_loan(loan_id, user_id)