from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.features.company.data.repository import CompanyRepository
from app.features.company.data.schemas import CompanyCreate, CompanyOverviewResponse, CompanyUpdate, CompanyResponse
from app.features.company.service.company_service import CompanyService
from app.db import get_db
from app.core.security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional, List

router = APIRouter(prefix="/companies", tags=["companies"])
limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="app/templates/company")

def get_company_service(db: Session = Depends(get_db)) -> CompanyService:
    repository = CompanyRepository(db)
    return CompanyService(repository, db)

@router.get("/create", response_class=HTMLResponse)
async def get_create_company_page(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("create_company.html", {"request": request})

@router.post("/", response_model=CompanyResponse)
async def create_company(
    request: Request,
    company: CompanyCreate,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    return company_service.create_company(company.name, current_user)

@router.put("/{company_id}", response_model=CompanyResponse)
@limiter.limit("5/minute")
async def update_company(
    request: Request,
    company_id: int,
    company: CompanyUpdate,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    return company_service.update_company(company_id, company.name, company.government_admin_id, company.is_active, current_user)

@router.delete("/{company_id}")
@limiter.limit("5/minute")
async def delete_company(
    request: Request,
    company_id: int,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    company_service.delete_company(company_id, current_user)
    return {"message": "Company deleted successfully"}

@router.get("/", response_model=List[CompanyResponse])
@limiter.limit("5/minute")
async def list_companies(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    return company_service.list_companies(current_user, page, per_page)

@router.get("/who_is")
@limiter.limit("10/minute")
async def who_is(
    request: Request,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    return company_service.who_is(current_user)
    
    
@router.get("/{company_id}/overview", response_model=CompanyOverviewResponse)
async def get_company_overview(
    company_id: int,
    company_service: CompanyService = Depends(get_company_service),
    current_user: dict = Depends(get_current_user)
):
    return company_service.get_company_overview(company_id, current_user)